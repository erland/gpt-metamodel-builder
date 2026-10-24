#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import canonical_value
vectors=json.loads((root/"interop/canonical-values-v1.json").read_text())
for kind,cases in vectors.items():
    if kind=="version":continue
    for case in cases:
        actual=canonical_value(kind,case["input"])
        expected={k:v for k,v in case.items() if k!="input"}
        assert actual==expected,(kind,case,actual)
print("PASS: Python canonical value profile")
