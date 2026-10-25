"""CORE-007 opt-in instance cardinality validation for explicit endpoint incidence.

A count describes the number of occurrences of a relationship type at one
specific endpoint instance. This helper does not infer a meaning for legacy data.
"""
from __future__ import annotations

import re


def parse_range(value: str) -> tuple[int, int | None]:
    if not isinstance(value, str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.\.(?:0|[1-9][0-9]*|\*))?|\*", value):
        raise ValueError("CORE-007 invalid cardinality")
    if value == "*":
        return 0, None
    parts = value.split("..")
    lower = int(parts[0])
    upper = None if len(parts) == 2 and parts[1] == "*" else int(parts[-1])
    if upper is not None and upper < lower:
        raise ValueError("CORE-007 inverted cardinality")
    return lower, upper


def validate_incidence(model: dict, counts: list[dict]) -> list[dict]:
    """Return deterministic violations; count entries are per (relation, role, instance).

    The caller explicitly supplies a complete population of endpoint instances.
    Omitted counts are never assumed to be zero.
    """
    rels = {rel["id"]: rel for rel in model["relationships"]}
    errors = []
    seen = set()
    for entry in counts:
        relation, role, ident, count = (entry.get("relationship"), entry.get("role"),
                                         entry.get("instance"), entry.get("count"))
        key = (relation, role, ident)
        if key in seen:
            raise ValueError("CORE-007 duplicate endpoint incidence key")
        seen.add(key)
        if relation not in rels or role not in ("source", "target") or not isinstance(ident, str) or not ident:
            raise ValueError("CORE-007 unknown relation, role or instance")
        if type(count) is not int or count < 0:
            raise ValueError("CORE-007 count must be nonnegative integer")
        card = rels[relation][role].get("cardinality")
        if card is None:
            raise ValueError("CORE-007 not_supported: unspecified endpoint cardinality")
        minimum, maximum = parse_range(card)
        if count < minimum or (maximum is not None and count > maximum):
            errors.append({"relationship": relation, "role": role, "instance": ident,
                           "count": count, "minimum": minimum, "maximum": maximum})
    return sorted(errors, key=lambda item: (item["relationship"], item["role"], item["instance"]))
