#!/usr/bin/env python3
"""Prevent unsupported release claims and orphaned generic evidence references."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
review=json.loads((ROOT/"conformance/mmp-generic-expressiveness-post-advanced.json").read_text())
assert review["status"]=="partial_no_go"
assert review["release_decision"]=="no_go"
assert review["legacy_format_unchanged"] is True
assert len(review["evidence"])>=6
ci=(ROOT/"scripts/run_ci.py").read_text()
ts=(ROOT/".github/workflows/mmp-typescript.yml").read_text()
for item in review["evidence"]:
 assert item["limitations"] and item["level"]
 path=ROOT/item["source"]
 assert path.is_file(),path
 assert path.name in ci,path.name
 assert path.name+" --typescript" in ts,path.name
assert {x["id"] for x in review["blockers"]}>={"CORE-007","CORE-009/011","CORE-012"}
print("Generic expressiveness evidence and NO-GO review PASS")
