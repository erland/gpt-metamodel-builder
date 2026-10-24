#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import classify_model_change,extension_support
f=json.loads((root/"interop/version-extension-v1.json").read_text())
for case in f["cases"]:
    assert classify_model_change(case["before"],case["after"])==case["expected"],case
for case in f["extensions"]:
    assert extension_support(case["extensions"],case["recognized"],case["critical"])==case["expected"],case
print("PASS: Python conservative version compatibility and extension policy")
