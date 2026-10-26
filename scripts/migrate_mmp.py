#!/usr/bin/env python3
"""Validated, non-destructive MMP 1.0 -> 1.1 format migration.

This operation does not invent MMP 1.1 relationship semantics. It repackages
the identical canonical YAML payload with a new, validated manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

from import_mmp import execute as import_execute
from export_mmp import export


def _canonical(package: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(package) as archive:
        return {name: archive.read(name) for name in archive.namelist()
                if name.startswith("canonical/") and name.endswith(".yaml")}


def migrate(source: Path, destination: Path, report_path: Path, producer_version: str = "dev") -> dict:
    source = source.resolve()
    destination = destination.resolve()
    report_path = report_path.resolve()
    if destination == report_path or destination == source or report_path == source:
        raise ValueError("Input package, output package and report must be distinct")
    if destination.exists() or report_path.exists():
        raise FileExistsError("Refusing to overwrite output package or migration report")

    inspected = import_execute(source, "inspect")
    if inspected["package_format_version"] != "1.0.0":
        raise ValueError("Expected a valid MMP 1.0.0 package")
    # Full integrity, offline JSON Schema and canonical semantic validation.
    import_execute(source, "validate")
    before = _canonical(source)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        model = work / "model"
        import_execute(source, "import", model)
        candidate = work / "migrated.mmp.zip"
        export(model, candidate, producer_version, candidate_1_1=True)
        verified = import_execute(candidate, "validate")
        after = _canonical(candidate)
        changed = [name for name, payload in before.items() if after.get(name) != payload]
        added = sorted(set(after) - set(before))
        if changed or any(name != "canonical/guidance.yaml" for name in added):
            raise ValueError("Canonical payload changed during migration; no output written")
        with tempfile.TemporaryDirectory() as tmp2:
            restored = Path(tmp2) / "restored"
            import_execute(candidate, "import", restored)
            for name, data in before.items():
                if (restored / Path(name).name).read_bytes() != data:
                    raise ValueError(f"Roundtrip mismatch: {name}")
        report = {
            "status": "pass",
            "migration": "MMP 1.0.0 -> 1.1.0",
            "mode": "lossless_format_only",
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "canonical_files_preserved": len(before),
            "canonical_payload_byte_identical": not added,
            "canonical_files_added": added,
            "added_guidance_is_template": bool(added),
            "semantic_enrichment_performed": False,
            "target_required_capabilities": [],
            "new_optional_features": [
                "typed endpoints", "exact typed relationship pairs",
                "junction profiles", "required/default presence profiles"
            ],
            "validation": {"source": "pass", "target": "pass",
                           "target_reimport": "pass"},
            "summary": verified["summary"],
            "note": "Optional semantic enrichment requires separate modeling decisions.",
        }
        # Commit only after all checks succeed. Preserve existing paths.
        destination.parent.mkdir(parents=True, exist_ok=True)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(candidate.read_bytes())
        try:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        except Exception:
            destination.unlink()
            raise
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Validated MMP 1.0 ZIP")
    parser.add_argument("--output", required=True, type=Path, help="New MMP 1.1 ZIP")
    parser.add_argument("--report", required=True, type=Path, help="New JSON migration report")
    parser.add_argument("--producer-version", default="dev")
    args = parser.parse_args()
    print(json.dumps(migrate(args.source, args.output, args.report, args.producer_version),
                     indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import sys
        print(f"MMP migration failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
