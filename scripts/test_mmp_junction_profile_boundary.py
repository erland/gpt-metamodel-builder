#!/usr/bin/env python3
"""CORE-016 profile boundary: standalone AND/OR metadata, no Core schema mutation."""
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/"schemas/mmp-junction-structure-profile.schema.json").read_text())
validator=Draft202012Validator(schema)
validator.check_schema(schema)
valid={"profile":"mmp-junction-structure@0.1.0","junction_operators":{"join_and":"and","choice_or":"or"}}
assert validator.is_valid(valid)
for bad in [
 {"profile":"mmp-junction-structure@0.1.0","junction_operators":{"join_and":"xor"}},
 {"profile":"mmp-junction-structure@0.1.0","junction_operators":{}},
 {"profile":"mmp-junction-structure@1.0.0","junction_operators":{"j":"and"}},
 {**valid,"unexpected":True},
]:
 assert not validator.is_valid(bad),bad
core=json.loads((ROOT/"schemas/metamodel.schema.json").read_text())
junction=core["$defs"]["junctionType"]
assert "operator" not in junction["properties"]
assert junction["additionalProperties"] is False
assert set(junction["required"])=={"id","name"}
print("CORE-016 profile separation PASS")
