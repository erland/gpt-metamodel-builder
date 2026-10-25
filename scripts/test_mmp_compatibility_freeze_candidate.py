#!/usr/bin/env python3
"""Candidate release-freeze scope/evidence integrity checks; not a release certificate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/"conformance/mmp-1-1-compatibility-freeze-candidate.json").read_text())
assert r["status"]=="proposed_release_freeze_not_published"
assert r["legacy_package_format"]=="1.0.0"
assert r["release_decision"]=="NO_GO_until_gates_pass"
assert {p["id"] for p in r["policies"]}=={"CORE-009","CORE-011","CORE-015/016"}
assert len(r["release_gates"])>=4
for p in r["policies"]:
 assert p["contract"] and p["deferred"]
 assert (ROOT/p["source"]).is_file(),p["source"]
assert "never silently alter older packages" in r["compatibility_principle"]
assert "not_supported" in (ROOT/"docs/mmp-1-1-compatibility-freeze-candidate.md").read_text()
ci=(ROOT/"scripts/run_ci.py").read_text()
for script in ("test_mmp_required_policy.py","test_mmp_canonical_values.py",
               "test_mmp_inherited_pairs_full_package.py"):
 assert script in ci,script
print("MMP 1.1 candidate compatibility-freeze scope integrity PASS")
