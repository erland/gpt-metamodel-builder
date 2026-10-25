"""CORE-016 opt-in bridge from a verified junction profile to structure checks.

This does not treat operator metadata as part of canonical MMP Core.
"""
from __future__ import annotations
from mmp_junction_structure import validate_junction_structure

def validate_profile_structure(model: dict, graph: dict, profile: dict) -> list[dict]:
    definitions = model.get("junctions", [])
    expected = {item["id"] for item in definitions}
    if (not isinstance(profile, dict)
            or set(profile) != {"profile", "junction_operators"}
            or profile["profile"] != "mmp-junction-structure@0.1.0"
            or not isinstance(profile["junction_operators"], dict)
            or set(profile["junction_operators"]) != expected
            or any(value not in ("and", "or") for value in profile["junction_operators"].values())):
        raise ValueError("CORE-016 not_supported: invalid negotiated junction profile")
    # Isolated projection only; never mutate source canonical definitions.
    projected = dict(model)
    projected["junctions"] = [
        {**item, "operator": profile["junction_operators"][item["id"]]}
        for item in definitions
    ]
    return validate_junction_structure(projected, graph)
