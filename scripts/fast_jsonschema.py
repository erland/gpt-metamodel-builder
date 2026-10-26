"""Fast, semantics-preserving uniqueItems validation for string-only JSON trees.

Large MMP typed-pair arrays contain deeply nested objects with string leaves.
The stock jsonschema uniqueItems check can perform quadratic comparisons.
For these JSON trees, deterministic canonical serialization provides the
same equality semantics. All other values fall back to jsonschema unchanged
(including numbers, where 1 and 1.0 compare equal, and booleans).
"""
import json

from jsonschema import Draft202012Validator, ValidationError, validators

_ORIGINAL_UNIQUE_ITEMS = Draft202012Validator.VALIDATORS["uniqueItems"]


def _string_tree(value):
    if isinstance(value, str):
        return True
    if isinstance(value, list):
        return all(_string_tree(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _string_tree(item)
                   for key, item in value.items())
    return False


def _fast_unique_items(validator, unique_items, instance, schema):
    if not unique_items or not isinstance(instance, list):
        yield from _ORIGINAL_UNIQUE_ITEMS(validator, unique_items, instance, schema)
        return
    if not all(_string_tree(item) for item in instance):
        yield from _ORIGINAL_UNIQUE_ITEMS(validator, unique_items, instance, schema)
        return

    seen = set()
    for item in instance:
        fingerprint = json.dumps(item, sort_keys=True, separators=(",", ":"),
                                 ensure_ascii=False)
        if fingerprint in seen:
            yield ValidationError("Array has non-unique elements")
            return
        seen.add(fingerprint)


FastDraft202012Validator = validators.extend(
    Draft202012Validator, {"uniqueItems": _fast_unique_items}
)
