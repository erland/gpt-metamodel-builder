#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"interop"))
from mmp_v1_consumer import parse_cardinality,required_profile
data=json.loads((ROOT/"interop/cardinality-v1.json").read_text())
for item in data["valid"]:
    assert parse_cardinality(item["text"])=={"min":item["min"],"max":item["max"]},item
for value in data["invalid"]:
    try: parse_cardinality(value)
    except ValueError: continue
    raise AssertionError(f"Invalid range accepted: {value}")
for item in data["required"]:
    assert required_profile(item["required"],item["cardinality"])==item["strict"],item
print("PASS: Python cardinality vectors and undecided required semantics")
