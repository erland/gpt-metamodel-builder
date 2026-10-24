#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import required_minimum_policy
for case in json.loads((root/"interop/required-policy-v1.json").read_text())["cases"]:
    actual=required_minimum_policy(case["required"],case["cardinality"])
    expected={k:v for k,v in case.items() if k not in ("required","cardinality")}
    assert actual==expected,(case,actual)
print("PASS: Python opt-in required minimum policy")
