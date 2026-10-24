#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import relationship_semantics
f=json.loads((root/"interop/relationship-semantics-v1.json").read_text())
summary,allowed=relationship_semantics(f["elements"],f["relationships"])
assert summary==f["expected"],(summary,f["expected"])
for case in f["cases"]:
    assert allowed(case["relationship"],case["source"],case["target"]) is case["allowed"],case
print("PASS: Python relationship role and subtype semantics")
