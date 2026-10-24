#!/usr/bin/env python3
"""Golden-vector test of Python Core effective properties."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import effective_properties
f=json.loads((root/"interop/effective-properties-v1.json").read_text())
got=effective_properties(f["elements"],f["relationships"],f["property_sets"],f["property_definitions"])
assert got==f["expected"],(got,f["expected"])
print("PASS: Python diamond-inheritance effective properties match golden semantics")
