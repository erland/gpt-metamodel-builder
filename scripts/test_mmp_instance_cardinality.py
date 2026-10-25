#!/usr/bin/env python3
"""CORE-007 instance cardinality candidate shared golden cases."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_instance_cardinality import validate_incidence
data=json.loads((ROOT/"interop/core007-instance-cardinality-v1.json").read_text())
for test in data["cases"]:
    try:
        violations=validate_incidence(test["model"],test["counts"])
        outcome="reject" if violations else "accept"
    except ValueError:
        outcome="not_supported" if test["expected"]=="not_supported" else "error"
    assert outcome==test["expected"],(test["id"],outcome,test["expected"])
print("CORE-007 instance cardinality candidate PASS")
