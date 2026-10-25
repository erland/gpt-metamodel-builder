#!/usr/bin/env python3
"""Shared CORE-007/016 typed graph golden vectors."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_typed_instance_graph import validate_typed_graph
vectors=json.loads((ROOT/"interop/core007-typed-graph-v1.json").read_text())
for case in vectors["cases"]:
    try:
        issues=validate_typed_graph(vectors["model"],case["graph"])
        actual="reject" if issues else "accept"
    except ValueError as e:
        actual="not_supported" if "not_supported" in str(e) else "error"
    assert actual==case["expected"],(case["id"],actual,case["expected"])
print("CORE-007/016 Python typed graph vectors PASS")
