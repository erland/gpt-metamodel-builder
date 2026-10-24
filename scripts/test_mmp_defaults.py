#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import validate_default_value
cases=json.loads((root/"interop/default-values-v1.json").read_text())["cases"]
for c in cases:
    got=validate_default_value(c["type"],c["value"],values=c.get("values"),cardinality=c.get("cardinality"))
    assert got is c["valid"],(c,got)
print(f"PASS: Python default semantics {len(cases)} vectors")
