#!/usr/bin/env python3
"""MMP semantic-upgrade planning is review-only and fails closed."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                          text=True, capture_output=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        model_dir = root / "model"
        shutil.copytree(ROOT / "examples/architecture-lite", model_dir)
        meta = model_dir / "metamodel.yaml"
        value = yaml.safe_load(meta.read_text())
        value["metamodel"]["namespace"] = "https://example.org/mmp-upgrade-plan"
        meta.write_text(yaml.safe_dump(value, sort_keys=False))
        source = root / "model.zip"
        result = run(ROOT / "scripts/export_mmp.py", "--model-dir", model_dir,
                     "--output", source)
        assert result.returncode == 0, result.stderr
        source_original = source.read_bytes()
        report = root / "plan.json"
        result = run(ROOT / "scripts/plan_mmp_upgrade.py", source,
                     "--output", report)
        assert result.returncode == 0, result.stderr
        plan = json.loads(report.read_text())
        assert plan["target_package_format"] == "1.1.0"
        assert plan["automatic_semantic_changes"] is False
        assert plan["review_required"] is True
        assert plan["recommendations"]
        assert all(x["selected_choice"] is None for x in plan["recommendations"])
        assert source.read_bytes() == source_original
        assert run(ROOT / "scripts/plan_mmp_upgrade.py", source,
                   "--output", report).returncode != 0
        assert run(ROOT / "scripts/plan_mmp_upgrade.py", root / "missing.zip",
                   "--output", root / "not-created.json").returncode != 0
        assert not (root / "not-created.json").exists()
    print("MMP semantic upgrade planning PASS")


if __name__ == "__main__":
    main()
