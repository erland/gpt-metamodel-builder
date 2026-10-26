#!/usr/bin/env python3
"""Check that new exports default to MMP 1.1 while legacy requires explicit opt-in."""
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "scripts/export_mmp.py"
MODEL = ROOT / "examples/architecture-lite"

def main():
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp) / "model"
        shutil.copytree(MODEL, source)
        model_file = source / "metamodel.yaml"
        model = yaml.safe_load(model_file.read_text())
        model["metamodel"]["namespace"] = "https://example.org/metamodels/archlite"
        model_file.write_text(yaml.safe_dump(model, sort_keys=False))
        for args, expected in (([], "1.1.0"), (["--legacy-1-0"], "1.0.0")):
            target = Path(temp) / f"{expected}.zip"
            result = subprocess.run(
                [sys.executable, str(EXPORT), "--model-dir", str(source),
                 "--output", str(target), *args],
                capture_output=True, text=True, cwd=ROOT,
            )
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
            with zipfile.ZipFile(target) as z:
                manifest = yaml.safe_load(z.read("manifest.yaml"))
            assert manifest["package_format_version"] == expected, manifest
    print("MMP 1.1 default and explicit 1.0 compatibility PASS")

if __name__ == "__main__":
    main()
