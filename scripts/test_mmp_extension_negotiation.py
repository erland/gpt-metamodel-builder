#!/usr/bin/env python3
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/"interop"))
from mmp_v1_consumer import negotiate_extensions
for c in json.loads((root/"interop/extension-negotiation-v1.json").read_text())["cases"]:
    assert negotiate_extensions(c["requirement"],c["consumer"])==c["expected"],c["name"]
print("PASS: Python versioned extension capability negotiation")
