#!/usr/bin/env python3
"""End-to-end CORE-015/016 integration, with an ArchiMate-inspired (not normative) model."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CAPS = [
    {"id": "mmp-pairwise-relationships", "version": "1.0.0"},
    {"id": "mmp-typed-endpoints", "version": "1.0.0"},
    {"id": "mmp-typed-pairs", "version": "1.0.0"},
]

def run(*args):
    return subprocess.run([str(x) for x in args], cwd=ROOT, text=True, capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        model = work / "model"
        shutil.copytree(ROOT / "examples/architecture-lite", model)
        source_file = model / "metamodel.yaml"
        data = yaml.safe_load(source_file.read_text(encoding="utf-8"))
        data["metamodel"]["namespace"] = "https://example.org/core015-core016/integration"
        data["metamodel"].setdefault("extensions", {})["mmp_required_capabilities"] = CAPS
        parent = data["relationships"][0]
        source = parent["source"]["types"][0]
        target = parent["target"]["types"][0]
        data["elements"].extend([
            {"id": "integration_source", "name": "Concrete source", "extends": [source]},
            {"id": "integration_target", "name": "Concrete target", "extends": [target]},
        ])
        parent["allowed_type_pairs"] = [{"source": source, "target": target}]
        second = {
            "id": "integration_second_parent", "name": "Restricted parent",
            "source": {"types": [source, "integration_source"]},
            "target": {"types": [target]},
            "allowed_type_pairs": [{"source": "integration_source", "target": target}],
        }
        child = {
            "id": "integration_child", "name": "Specialized relation",
            "extends": [parent["id"], second["id"]],
            "source": {"types": ["integration_source"]},
            "target": {"types": [target]},
        }
        data["relationships"].extend([second, child])
        data["junctions"] = [{"id": "integration_and", "name": "AND junction"}]
        typed = {
            "id": "integration_link", "name": "Link to relationship and junction",
            "source": {
                "types": [source],
                "typed_refs": [{"kind": "element", "id": source}, {"kind": "junction", "id": "integration_and"}],
            },
            "target": {
                "types": [],
                "typed_refs": [{"kind": "relationship", "id": "integration_child"}],
            },
            "allowed_typed_pairs": [{
                "source": {"kind": "junction", "id": "integration_and"},
                "target": {"kind": "relationship", "id": "integration_child"},
            }],
        }
        data["relationships"].append(typed)
        source_file.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
        original = source_file.read_bytes()

        # A candidate containing all three critical profiles must survive export/import.
        package = work / "combined.zip"
        result = run(sys.executable, ROOT / "scripts/export_mmp.py",
                     "--candidate-1-1", "--model-dir", model, "--output", package)
        assert result.returncode == 0, result.stderr
        assert run(sys.executable, ROOT / "scripts/import_mmp.py", "validate", package).returncode == 0
        import zipfile
        with zipfile.ZipFile(package) as archive:
            manifest = yaml.safe_load(archive.read("manifest.yaml"))
        assert manifest["required_capabilities"] == CAPS

        sys.path.insert(0, str(ROOT / "interop"))
        sys.path.insert(0, str(ROOT / "scripts"))
        from mmp_v1_consumer import consume
        from mmp_effective_pairs import effective_pairs
        expected = effective_pairs(data, "integration_child")
        python_result = consume(package)
        assert python_result["effective_pairs"]["integration_child"] == expected
        assert {(item["source"], item["target"]) for item in expected} == {
            ("integration_source", target),
            ("integration_source", "integration_target"),
        }
        if "--typescript" in sys.argv:
            node = ROOT / "interop/typescript/dist/consumer.js"
            assert node.is_file(), "Build TypeScript before --typescript run"
            ts = run("node", node, package)
            assert ts.returncode == 0, ts.stderr
            typescript_result = json.loads(ts.stdout)
            assert typescript_result["effective_pairs"] == python_result["effective_pairs"]

        imported = work / "imported"
        outcome = run(sys.executable, ROOT / "scripts/import_mmp.py",
                      "import", package, "--output", imported)
        assert outcome.returncode == 0, outcome.stderr
        assert (imported / "metamodel.yaml").read_bytes() == original
        assert source_file.read_bytes() == original

        # Reject loss of critical semantics when attempting legacy export.
        old = work / "old.zip"
        rejected = run(sys.executable, ROOT / "scripts/export_mmp.py",
                       "--model-dir", model, "--output", old)
        assert rejected.returncode != 0 and not old.exists(), rejected.stderr

        # Each critical capability must be explicit, not assumed from other features.
        for capability in CAPS:
            changed = yaml.safe_load(original)
            changed["metamodel"]["extensions"]["mmp_required_capabilities"] = [
                cap for cap in CAPS if cap != capability
            ]
            source_file.write_text(yaml.safe_dump(changed, sort_keys=False))
            target_file = work / (capability["id"] + ".zip")
            failed = run(sys.executable, ROOT / "scripts/export_mmp.py",
                         "--candidate-1-1", "--model-dir", model, "--output", target_file)
            assert failed.returncode != 0 and not target_file.exists(), (capability, failed.stderr)

        source_file.write_bytes(original)
        assert source_file.read_bytes() == original
    print("CORE-015/016 integrated candidate acceptance PASS")

if __name__ == "__main__":
    main()
