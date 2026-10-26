#!/usr/bin/env python3
"""End-to-end MMP export tests, including binary reproducibility and error paths."""
from __future__ import annotations
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "scripts/export_mmp.py"
SCHEMA = json.loads((ROOT / "schemas/mmp-manifest-v1.schema.json").read_text())


def cmd(*args, env=None):
    return subprocess.run([sys.executable, str(EXPORT), "--legacy-1-0", *map(str, args)],
                          text=True, capture_output=True, cwd=ROOT, env=env)


def check_payload(files):
    manifest = yaml.safe_load(files["manifest.yaml"])
    Draft202012Validator(SCHEMA, format_checker=FormatChecker()).validate(manifest)
    assert len(manifest["entrypoints"]) == 8
    listed = {item["path"]: item for item in manifest["files"]}
    assert set(files) - {"manifest.yaml"} == set(listed)
    for name, metadata in listed.items():
        assert hashlib.sha256(files[name]).hexdigest() == metadata["sha256"], name
    assert manifest["metamodel"]["namespace"] == "https://example.org/metamodels/architecture-lite"
    assert "schemas/common-definitions.schema.json" in listed
    return manifest


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "source"
        shutil.copytree(ROOT / "examples/architecture-lite", src)
        mm = src / "metamodel.yaml"
        content = yaml.safe_load(mm.read_text())
        content["metamodel"]["namespace"] = "https://example.org/metamodels/architecture-lite"
        mm.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True))
        env = {**os.environ, "SOURCE_DATE_EPOCH": "1792843200"}
        z1, z2, directory = root/"a.mmp.zip", root/"b.mmp.zip", root/"unpacked"
        common = ["--model-dir", src, "--producer-version", "1.2.2"]
        for output, extra in [(z1, []), (z2, []), (directory, ["--directory"])]:
            p = cmd(*common, "--output", output, *extra, env=env)
            assert p.returncode == 0, p.stdout+p.stderr
        assert z1.read_bytes() == z2.read_bytes(), "Fixed-clock ZIP is not bitwise reproducible"
        with zipfile.ZipFile(z1) as z:
            assert z.testzip() is None
            names = z.namelist()
            assert names == sorted(names)
            zipped = {name: z.read(name) for name in names}
        unpacked = {p.relative_to(directory).as_posix(): p.read_bytes()
                    for p in directory.rglob("*") if p.is_file()}
        assert zipped == unpacked, "Directory and ZIP payloads differ"
        check_payload(zipped)
        mm.write_text(mm.read_text().replace("https://example.org/metamodels/architecture-lite", "not-a-uri"))
        negative = cmd(*common, "--output", root/"bad.mmp.zip", env=env)
        assert negative.returncode != 0 and "namespace" in negative.stderr, negative.stderr
        assert not (root/"bad.mmp.zip").exists()
        again = cmd(*common, "--output", z1, env=env)
        assert again.returncode != 0, "Existing output overwritten"
    print("MMP export PASS: validated ZIP+directory; hash inventory; deterministic bytes; two negative cases")


if __name__ == "__main__":
    main()
