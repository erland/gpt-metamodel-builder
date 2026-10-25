#!/usr/bin/env python3
"""CORE-016 shared Python/TypeScript inherited instance-edge acceptance."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_typed_instance_graph import validate_typed_graph
vectors=json.loads((ROOT/"interop/core016-inherited-instance-graph-v1.json").read_text())
for case in vectors["cases"]:
 try:
  actual="reject" if validate_typed_graph(case.get("model",vectors["model"]),case["graph"]) else "accept"
 except ValueError as exc:
  actual="not_supported" if "not_supported" in str(exc) else "error"
 assert actual==case["expected"],(case["id"],actual,case["expected"])
print("CORE-016 inherited instance graph vectors Python PASS")
