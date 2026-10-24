#!/usr/bin/env python3
"""Verify stable MMP type identities across label changes and namespace evolution."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "scripts/export_mmp.py"
CONSUMER = ROOT / "interop/mmp_v1_consumer.py"


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, "SOURCE_DATE_EPOCH": "1792843200"})


def exported(source, output):
    result = run(EXPORT, "--model-dir", source, "--output", output)
    assert result.returncode == 0, result.stderr
    result = run(CONSUMER, output)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def identity(namespace, local_id):
    return namespace + "#" + quote(local_id, safe="-._~")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        source = base / "model"
        shutil.copytree(ROOT / "examples/architecture-lite", source)
        path = source / "metamodel.yaml"
        original = yaml.safe_load(path.read_text(encoding="utf-8"))
        namespace = "https://example.org/metamodels/architecture-lite"
        original["metamodel"]["namespace"] = namespace
        path.write_text(yaml.safe_dump(original, sort_keys=False, allow_unicode=True), encoding="utf-8")
        before = exported(source, base / "before.mmp.zip")
        changed = yaml.safe_load(path.read_text(encoding="utf-8"))
        changed["elements"][0]["name"] = "Renamed display label"
        changed["relationships"][0]["name"] = "Changed relationship label"
        path.write_text(yaml.safe_dump(changed, sort_keys=False, allow_unicode=True), encoding="utf-8")
        after = exported(source, base / "after.mmp.zip")
        for collection in ("elements", "relationships"):
            old = {x["id"]: identity(before["metamodel"]["namespace"], x["id"]) for x in before[collection]}
            new = {x["id"]: identity(after["metamodel"]["namespace"], x["id"]) for x in after[collection]}
            assert old == new, f"Label-only change altered {collection} identities"
        assert before["elements"][0]["name"] != after["elements"][0]["name"]
        changed["metamodel"]["namespace"] = "https://example.org/metamodels/new-domain"
        path.write_text(yaml.safe_dump(changed, sort_keys=False, allow_unicode=True), encoding="utf-8")
        moved = exported(source, base / "namespace-changed.mmp.zip")
        for collection in ("elements", "relationships"):
            old = {identity(namespace, x["id"]) for x in after[collection]}
            new = {identity(moved["metamodel"]["namespace"], x["id"]) for x in moved[collection]}
            assert old.isdisjoint(new), "Namespace migration unexpectedly preserved global identity"
        assert identity("https://example.org/mm", "a b") == "https://example.org/mm#a%20b"
        print("MMP identity evolution PASS: label rename stable; namespace change distinct; RFC3986 escaping")


if __name__ == "__main__":
    main()
