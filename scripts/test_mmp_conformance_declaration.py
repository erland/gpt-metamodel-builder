#!/usr/bin/env python3
"""Offline validation of draft MMP conformance declarations and rejection tests."""
from pathlib import Path
import copy, json
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/"schemas/mmp-conformance-declaration-v1.schema.json").read_text())
Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema)
original=json.loads((ROOT/"examples/mmp-consumer-conformance.json").read_text())
validator.validate(original)
cases=[]
wrong=copy.deepcopy(original);wrong["profiles"]["mmp-core"]["status"]="partial";wrong["profiles"]["mmp-core"].pop("limitations");cases.append(wrong)
wrong=copy.deepcopy(original);wrong["profiles"]["mmp-rules"]["status"]="evaluated";cases.append(wrong)
wrong=copy.deepcopy(original);wrong["profiles"]["unexpected"]={"status":"supported"};cases.append(wrong)
wrong=copy.deepcopy(original);wrong["package_format_versions"]=[];cases.append(wrong)
wrong=copy.deepcopy(original);wrong["implementation"]["role"]="other";cases.append(wrong)
for i,case in enumerate(cases):
    if validator.is_valid(case): raise AssertionError(f"Invalid case {i} accepted")
print("PASS: conformance declaration schema, example, 5 negative fixtures")
