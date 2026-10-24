#!/usr/bin/env python3
"""Real offline smoke tests for the portable Metamodel Builder domain engine.

Run from any working directory after unpacking the engine ZIP.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ["scripts/validate_canonical_schema.py"],
    ["scripts/test_semantic_validator.py"],
    ["scripts/test_sparx_mapping.py"],
    ["scripts/test_mdg_generator.py"],
    ["scripts/test_mdg_validation.py"],
    ["scripts/test_workspace_resume.py"],
    ["scripts/test_mmp_manifest_contract.py"],
    ["scripts/test_mmp_export.py"],
    ["scripts/test_mmp_import.py"],
    ["scripts/test_mmp_interop.py"],
    ["scripts/test_mmp_consumer_security.py"],
    ["scripts/test_mmp_consumer_semantics.py"],
]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    results = []
    for parts in CASES:
        command = [sys.executable, *parts]
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        record = {"command": parts, "exit_code": proc.returncode,
                  "stdout": proc.stdout[-5000:], "stderr": proc.stderr[-5000:]}
        results.append(record)
        print(f"{'PASS' if proc.returncode == 0 else 'FAIL'}: {' '.join(parts)}", flush=True)
    report = {"status": "PASS" if all(r["exit_code"] == 0 for r in results) else "FAIL",
              "checks": results}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if report["status"] == "FAIL":
        for r in results:
            if r["exit_code"]:
                print(r["stderr"] or r["stdout"], file=sys.stderr)
    return 0 if report["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
