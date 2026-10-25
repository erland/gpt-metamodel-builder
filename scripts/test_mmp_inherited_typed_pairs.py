#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_effective_typed_pairs import effective_typed_pairs
suite=json.loads((ROOT/"interop/core016-inherited-typed-pairs-v1.json").read_text())
for item in suite["cases"]:
 try:
  result=effective_typed_pairs(item["model"],item["relationship"])
  outcome="accept"
 except ValueError as exc:
  outcome="not_supported" if "not_supported" in str(exc) else "error"
 assert outcome==item["expected"],(item["id"],outcome,item["expected"])
 if outcome=="accept":assert result==item["pairs"],(item["id"],result,item["pairs"])
print("CORE-016 inherited typed pairs Python PASS")
