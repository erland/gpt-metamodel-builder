#!/usr/bin/env python3
"""Regression gate for factual claims in MMP Core 1.1 compatibility review.

These checks document what the *published* 1.0.0 schemas allow. They do not
change validation policy or claim new Core conformance.
"""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
common=json.loads((ROOT/"schemas/common-definitions.schema.json").read_text())
props=json.loads((ROOT/"schemas/properties.schema.json").read_text())
model=json.loads((ROOT/"schemas/metamodel.schema.json").read_text())
rules=json.loads((ROOT/"schemas/constraints.schema.json").read_text())
cardinality=Draft202012Validator(common["$defs"]["cardinality"])
assert cardinality.is_valid("3..1"), "1.0.0 cardinality schema has unexpectedly changed"
assert cardinality.is_valid("0..*")
assert not cardinality.is_valid("2..x")
p=props["properties"]["property_definitions"]["items"]["properties"]
assert p["default"]=={}, "1.0.0 default is no longer unconstrained"
assert p["required"]["type"]=="boolean"
assert p["cardinality"]["$ref"].endswith("/cardinality")
assert model["$defs"]["elementType"]["properties"]["extends"]["$ref"].endswith("/refList")
assert model["$defs"]["relationshipType"]["properties"]["directed"]["default"] is True
assert common["$defs"]["extensions"]["additionalProperties"] is True
rule_lang=rules["properties"]["constraints"]["items"]["properties"]["rule"]["properties"]["language"]["enum"]
assert set(rule_lang)=={"declarative","ocl","expression","natural_language"}
print("PASS: published MMP 1.0.0 schema permits documented compatibility edge cases")
