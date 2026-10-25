#!/usr/bin/env python3
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_junction_structure import validate_junction_structure
suite=json.loads((ROOT/"interop/core016-junction-structure-v1.json").read_text())
for case in suite["cases"]:
 try:
  problems=validate_junction_structure(suite["model"],case["graph"])
  actual="reject" if problems else "accept"
 except ValueError as exc:
  actual="not_supported" if "not_supported" in str(exc) else "error"
 assert actual==case["expected"],(case["id"],actual,case["expected"])
print("CORE-016 Python junction structure PASS")
