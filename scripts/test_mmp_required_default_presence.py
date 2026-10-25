#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/"scripts"))
from mmp_required_default_presence import decide
data=json.loads((root/"interop/required-default-presence-v1.json").read_text())
assert data["status"]=="candidate_opt_in"
for case in data["cases"]:
 result=decide(case)
 assert result==case["expected"],(case["id"],result,case["expected"])
print("Required/default candidate contract PASS")
