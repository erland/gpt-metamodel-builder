#!/usr/bin/env python3
"""Integrity of the limited-release decision and source evidence, not certification."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/"conformance/mmp-11-limited-release-decision.json").read_text())
assert r["decision"]=="conditional_no_go"
assert r["candidate_profile_gate"]["profiles"]==7
assert (ROOT/r["candidate_profile_gate"]["path"]).is_file()
assert {b["id"] for b in r["release_blockers"]}=={"RELEASE-01","RELEASE-02","RELEASE-03","RELEASE-04"}
assert all(b["status"]=="open" for b in r["release_blockers"])
assert r["go_condition"] and r["deferred_nonblocking"]
assert "test_mmp_11_candidate_release_gate.py" in (ROOT/"scripts/run_ci.py").read_text()
assert "test_mmp_11_candidate_release_gate.py --typescript" in (ROOT/".github/workflows/mmp-typescript.yml").read_text()
print("MMP 1.1 scoped release decision integrity PASS (conditional NO-GO)")
