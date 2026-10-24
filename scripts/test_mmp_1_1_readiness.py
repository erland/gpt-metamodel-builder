#!/usr/bin/env python3
"""Check readiness inventory evidence and guard against unsupported 1.1 release claims."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"conformance/mmp-1-1-readiness.json").read_text(encoding="utf-8"))
assert data["review_version"]=="1.0.0"
assert data["source_contract_version"]=="1.0.0"
assert data["target_format_version"]=="1.1.0"
assert data["overall"]=="not_ready"
rows=data["requirements"]
assert len(rows)==14 and len({r["id"] for r in rows})==14
assert {r["id"] for r in rows}=={f"CORE-{i:03d}" for i in range(1,15)}
for row in rows:
    assert row["status"] in ("covered_subset","open","decision_required")
    assert isinstance(row["limitation"],str) and row["limitation"].strip()
    assert row["evidence"]
    for name in row["evidence"]:
        p=ROOT/name
        assert p.is_file() and p.resolve().is_relative_to(ROOT), (row["id"],name)
assert {r["id"] for r in rows if r["status"]=="decision_required"} >= {"CORE-009","CORE-011","CORE-013"}
assert len(data["release_blockers"])>=5
assert {p["id"] for p in data["optional_profiles"]} == {"mmp-rules","mmp-notation","mmp-viewpoints"}
assert all(p["status"]=="not_verified" for p in data["optional_profiles"])
for name in data["implementation_evidence"].values():
    assert (ROOT/name).is_file(), name
print("PASS: 14 traceable MMP Core requirements, unresolved blockers and guarded NO-GO")
