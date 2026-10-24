#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import relation_inheritance_profile
f=json.loads((root/"interop/relationship-inheritance-v1.json").read_text())
for case in f["cases"]:
    actual=relation_inheritance_profile(f["elements"],case["relations"])
    assert actual==case["expected"],(case["id"],actual,case["expected"])
print("PASS: Python relation inheritance profile vectors")
