#!/usr/bin/env python3
"""Approved MMP upgrades: explicit pair decisions, unchanged source, fail closed."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import yaml

ROOT = Path(__file__).resolve().parents[1]
def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                          text=True, capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        model = root / "model"
        shutil.copytree(ROOT / "examples/architecture-lite", model)
        path = model / "metamodel.yaml"
        doc = yaml.safe_load(path.read_text())
        doc["metamodel"]["namespace"] = "https://example.org/mmp-upgrade-apply"
        path.write_text(yaml.safe_dump(doc, sort_keys=False))
        source = root / "source.zip"
        exported = run(ROOT/"scripts/export_mmp.py", "--model-dir", model, "--output", source)
        assert exported.returncode == 0, exported.stderr
        original = source.read_bytes()
        decisions = root / "decisions.json"
        generated = run(ROOT/"scripts/plan_mmp_upgrade.py", source, "--output", decisions)
        assert generated.returncode == 0, generated.stderr
        review = json.loads(decisions.read_text())
        rid = review["decisions"][0]["relationship_id"]
        relation = next(rel for rel in doc["relationships"] if rel["id"] == rid)
        chosen = review["decisions"][0]
        chosen["choice"] = "specify_explicit_rules"
        chosen["allowed_type_pairs"] = [{
            "source": relation["source"]["types"][0],
            "target": relation["target"]["types"][0]}]
        chosen["evidence"] = "Explicitly approved in this test"
        decisions.write_text(json.dumps(review))
        target = root / "approved.zip"
        report = root / "audit.json"
        applied = run(ROOT/"scripts/apply_mmp_upgrade.py", source, "--decisions",
                      decisions, "--output", target, "--report", report)
        assert applied.returncode == 0, applied.stderr
        audit = json.loads(report.read_text())
        assert audit["changed_relationships"] == 1
        assert source.read_bytes() == original
        assert run(ROOT/"scripts/import_mmp.py", "validate", target).returncode == 0
        with zipfile.ZipFile(target) as z:
            upgraded = yaml.safe_load(z.read("canonical/metamodel.yaml"))
        updated_rel = next(r for r in upgraded["relationships"] if r["id"] == rid)
        assert updated_rel["allowed_type_pairs"] == chosen["allowed_type_pairs"]
        # Refuse overwrite, stale review and fabricated out-of-domain pair.
        assert run(ROOT/"scripts/apply_mmp_upgrade.py", source, "--decisions",
                   decisions, "--output", target, "--report", report).returncode != 0
        review["source_sha256"] = "0" * 64
        decisions.write_text(json.dumps(review))
        invalid = root / "invalid.zip"
        assert run(ROOT/"scripts/apply_mmp_upgrade.py", source, "--decisions",
                   decisions, "--output", invalid, "--report", root/"invalid.json").returncode != 0
        assert not invalid.exists()
        review["source_sha256"] = audit["source_sha256"]
        review["decisions"][0]["allowed_type_pairs"][0]["source"] = "not-a-type"
        decisions.write_text(json.dumps(review))
        assert run(ROOT/"scripts/apply_mmp_upgrade.py", source, "--decisions",
                   decisions, "--output", invalid, "--report", root/"invalid.json").returncode != 0
        assert not invalid.exists()
    print("Approved MMP semantic upgrade PASS")

if __name__ == "__main__":
    main()
