#!/usr/bin/env python3
"""Verify source-based MMP 1.1 CORE-007/016 review evidence and release gate."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/"conformance/mmp-1-1-core007-016-review-20261025.json").read_text())
assert report["decision"]=="no_go"
assert report["legacy_mmp_1_0_unchanged"] is True
assert "not external certification" in report["evidence_level"]
assert (ROOT/report["historical_baseline"]).is_file()
assert {a["id"] for a in report["assessment"]}=={"CORE-007","CORE-016"}
for area in report["assessment"]:
 assert area["status"]=="candidate_subset"
 assert area["implemented"] and area["gaps"] and area["evidence"]
 for path in area["evidence"]:
  assert (ROOT/path).is_file(),path
assert len(report["cross_cutting_blockers"])>=3
# Ensure the review references tests actively registered in CI rather than just orphaned scripts.
ci=(ROOT/"scripts/run_ci.py").read_text()
ts=(ROOT/".github/workflows/mmp-typescript.yml").read_text()
for script in ["test_mmp_typed_graph_vectors.py","test_mmp_junction_package_profile.py","test_mmp_junction_profile_graph_package.py"]:
 assert script in ci,script
for script in ["typed-graph-test.js","test_mmp_junction_profile_graph_package.py --typescript"]:
 assert script in ts,script
# The Python package runner invokes the TS graph evaluator with package-extracted data.
package_runner=(ROOT/"scripts/test_mmp_junction_profile_graph_package.py").read_text()
assert "junction-profile-graph-test.js" in package_runner
assert "mmp_1_0_0_unchanged" in (ROOT/"project-status.yaml").read_text()
print("Post-PR76 CORE-007/016 review integrity PASS (NOT normative certification)")
