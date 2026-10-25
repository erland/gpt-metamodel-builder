#!/usr/bin/env python3
"""Fail closed on missing coverage evidence; never turn subset PASS into release approval."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
data=json.loads((root/"conformance/strict-core-coverage-v1.json").read_text(encoding="utf-8"))
ready=json.loads((root/"conformance/mmp-1-1-readiness.json").read_text(encoding="utf-8"))
assert data["version"]=="0.1.0" and data["profile"]=="strict-core-candidate"
assert data["format"]=="1.0.0" and data["overall"]=="partial"
assert data["release_decision"]=="NO-GO" and ready["overall"]=="not_ready"
requirements={x["id"] for x in ready["requirements"]}
covered=set()
for item in data["coverage"]:
    assert item["status"]=="subset" and item["check"]
    assert (root/item["evidence"]).is_file(),item
    for requirement in item["requirements"]:
        assert requirement in requirements,requirement
        covered.add(requirement)
gaps=set()
for item in data["gaps"]:
    assert item["id"] in requirements and item["gap"].strip()
    gaps.add(item["id"])
assert covered | gaps==requirements,requirements-covered-gaps
assert {"CORE-010","CORE-011","CORE-013"} <= gaps
assert "full" not in {x["status"] for x in data["coverage"]}
print("PASS: strict candidate coverage is evidence-backed, partial, and release blocked")
