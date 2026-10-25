#!/usr/bin/env python3
"""Single executable, scoped MMP 1.1 candidate profile acceptance gate.

Runs actual package-level tests, not just source presence checks. This is NOT
full Core conformance certification; individual scripts own negative cases.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("pairwise-relationships", "scripts/test_mmp_effective_pairs_package.py"),
    ("typed-endpoints", "scripts/test_mmp_typed_endpoints_package.py"),
    ("typed-pairs", "scripts/test_mmp_typed_pair_package.py"),
    ("inherited-typed-pairs", "scripts/test_mmp_inherited_pairs_full_package.py"),
    ("junction-structure", "scripts/test_mmp_junction_package_profile.py"),
    ("junction-graph", "scripts/test_mmp_junction_profile_graph_package.py"),
    ("required-default-presence", "scripts/test_mmp_required_default_package.py"),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--typescript", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    results = []
    for name, path in CASES:
        cmd = [sys.executable, str(ROOT / path)]
        if args.typescript:
            cmd.append("--typescript")
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        results.append({
            "profile": name,
            "script": path,
            "result": "pass" if proc.returncode == 0 else "fail",
            "exit_code": proc.returncode,
            "mode": "python+typescript" if args.typescript else "python",
        })
        print(f"{name}: {results[-1]['result']}", flush=True)
        if proc.returncode:
            print((proc.stdout + "\n" + proc.stderr)[-4500:], file=sys.stderr, flush=True)
    report = {
        "scope": "MMP 1.1 candidate declared-profile package acceptance subset",
        "release_decision": "NOT_A_FULL_CORE_GO",
        "legacy_1_0_regression": "separate CI suite",
        "all_pass": all(r["result"] == "pass" for r in results),
        "results": results,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"all_pass": report["all_pass"], "checked": len(results),
                      "release_decision": report["release_decision"]}))
    return 0 if report["all_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
