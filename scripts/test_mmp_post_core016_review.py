#!/usr/bin/env python3
"""Review gate: evidence pointers must exist; NO-GO must not be reported as GO."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
review=json.loads((ROOT/"conformance/mmp-1-1-post-core016-review.json").read_text())
assert review["decision"]=="no_go"
assert review["legacy_mmp_1_0_unchanged"] is True
assert review["release_blockers"]
assert (ROOT/review["historical_baseline"]).is_file()
for area in review["areas"]:
    assert area["id"] and area["evidence"],area
    for evidence in area["evidence"]:
        assert (ROOT/evidence).is_file(),evidence
assert len({area["id"] for area in review["areas"]})==len(review["areas"])
print("MMP 1.1 review evidence integrity PASS (not a normative conformance test)")
