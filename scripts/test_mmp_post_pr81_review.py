#!/usr/bin/env python3
"""Post PR81 CORE-015/016 release-review provenance, not normative certification."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/"conformance/mmp-1-1-post-pr81-core015-016.json").read_text())
assert r["decision"]=="no_go" and r["legacy_mmp_1_0_unchanged"] is True
assert "not external certification" in r["evidence_level"]
assert (ROOT/r["historical_baseline"]).is_file()
assert {x["id"] for x in r["areas"]}=={"CORE-015","CORE-016"}
for item in r["areas"]:
 assert item["status"]=="candidate_subset" and item["implemented"] and item["open"]
 for path in item["evidence"]:assert (ROOT/path).is_file(),path
assert len(r["cross_cutting_blockers"])>=3
ci=(ROOT/"scripts/run_ci.py").read_text()
ts=(ROOT/".github/workflows/mmp-typescript.yml").read_text()
assert "test_mmp_inherited_pairs_full_package.py" in ci
assert "test_mmp_inherited_pairs_full_package.py --typescript" in ts
assert "typed-graph-test.js" in (ROOT/"scripts/test_mmp_inherited_pairs_full_package.py").read_text()
print("Post-PR81 CORE-015/016 evidence and NO-GO integrity PASS")
