#!/usr/bin/env python3
"""End-to-end format migration and fail-closed regression."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "scripts/export_mmp.py"
MIGRATE = ROOT / "scripts/migrate_mmp.py"
IMPORT = ROOT / "scripts/import_mmp.py"


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], cwd=ROOT,
                          text=True, capture_output=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src = root / "canonical"
        shutil.copytree(ROOT / "examples/architecture-lite", src)
        f = src / "metamodel.yaml"
        model = yaml.safe_load(f.read_text())
        model["metamodel"]["namespace"] = "https://example.org/test/mmp-migration"
        f.write_text(yaml.safe_dump(model, sort_keys=False))
        old = root / "original.mmp.zip"
        assert run(EXPORT, "--legacy-1-0", "--model-dir", src,
                   "--output", old).returncode == 0
        original_bytes = old.read_bytes()
        new, report = root / "new.mmp.zip", root / "migration.json"
        migrated = run(MIGRATE, old, "--output", new, "--report", report)
        assert migrated.returncode == 0, migrated.stderr
        result = json.loads(report.read_text())
        assert result["status"] == "pass"
        assert result["semantic_enrichment_performed"] is False
        assert result["canonical_files_preserved"] >= 7
        assert original_bytes == old.read_bytes()
        with zipfile.ZipFile(new) as archive:
            manifest = yaml.safe_load(archive.read("manifest.yaml"))
            assert manifest["package_format_version"] == "1.1.0"
            assert manifest["required_capabilities"] == []
        assert run(IMPORT, "validate", new).returncode == 0
        # Never overwrite an existing target or report.
        assert run(MIGRATE, old, "--output", new, "--report", report).returncode != 0
        # Wrong input version is refused.
        assert run(MIGRATE, new, "--output", root/"invalid.zip",
                   "--report", root/"invalid.json").returncode != 0
        assert not (root/"invalid.zip").exists()
        # Tampered source is rejected before creating output files.
        with zipfile.ZipFile(old) as z:
            payload = {name: z.read(name) for name in z.namelist()}
        payload["canonical/version.yaml"] += b"\n# modified\n"
        bad = root/"tampered.zip"
        with zipfile.ZipFile(bad, "w") as z:
            for name, data in payload.items():
                z.writestr(name, data)
        blocked = root/"blocked.zip"
        blocked_report = root/"blocked.json"
        assert run(MIGRATE, bad, "--output", blocked,
                   "--report", blocked_report).returncode != 0
        assert not blocked.exists() and not blocked_report.exists()
    print("MMP 1.0 -> 1.1 migration PASS: validated roundtrip, original unchanged, fail-closed")


if __name__ == "__main__":
    main()
