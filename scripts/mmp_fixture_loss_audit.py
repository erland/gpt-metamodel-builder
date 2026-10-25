"""Deterministic type-and-pair inventory and strict roundtrip loss assessment."""
from __future__ import annotations
from collections import Counter
import hashlib
import json

COLLECTIONS = ("elements", "relationships", "junctions")

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()

def inventory(document):
    result = {"collections": {}, "pairs": {}, "total_pairs": 0}
    for category in COLLECTIONS:
        items = document.get(category, [])
        if not isinstance(items, list):
            raise ValueError(f"Invalid {category} collection")
        ids = [item["id"] for item in items]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate {category} IDs")
        # Sort by identifier, not file order, to measure content preservation.
        by_id = {item["id"]: item for item in items}
        result["collections"][category] = {
            "count": len(items),
            "ids": sorted(ids),
            "digest": digest([by_id[ident] for ident in sorted(ids)])
        }
    for rel in document.get("relationships", []):
        typed = rel.get("allowed_typed_pairs", [])
        basic = rel.get("allowed_type_pairs", [])
        if typed and basic:
            raise ValueError("Multiple pair schemes on one relationship")
        pairs = typed or basic
        serialized = [canonical(p) for p in pairs]
        if len(serialized) != len(set(serialized)):
            raise ValueError("Duplicate declared pair")
        result["pairs"][rel["id"]] = {
            "count": len(pairs),
            "digest": digest(sorted(serialized)),
            "keys": sorted(serialized),
        }
        result["total_pairs"] += len(pairs)
    return result

def compare(original, restored):
    before, after = inventory(original), inventory(restored)
    losses = []
    for category in COLLECTIONS:
        left, right = before["collections"][category], after["collections"][category]
        left_ids, right_ids = set(left["ids"]), set(right["ids"])
        for ident in sorted(left_ids-right_ids):
            losses.append({"kind": category, "id": ident, "change": "missing"})
        for ident in sorted(right_ids-left_ids):
            losses.append({"kind": category, "id": ident, "change": "unexpected"})
        if left["digest"] != right["digest"] and left_ids == right_ids:
            losses.append({"kind": category, "change": "content_changed"})
    for relid in sorted(set(before["pairs"]) | set(after["pairs"])):
        old = set(before["pairs"].get(relid, {}).get("keys", []))
        new = set(after["pairs"].get(relid, {}).get("keys", []))
        if old != new:
            losses.append({"kind": "relationship_pairs", "id": relid,
                           "change": "pair_set_changed",
                           "missing": len(old-new), "unexpected": len(new-old)})
    return {
        "status": "pass" if not losses else "fail",
        "original": {"elements": before["collections"]["elements"]["count"],
                     "relationships": before["collections"]["relationships"]["count"],
                     "junctions": before["collections"]["junctions"]["count"],
                     "pairs": before["total_pairs"]},
        "restored": {"elements": after["collections"]["elements"]["count"],
                     "relationships": after["collections"]["relationships"]["count"],
                     "junctions": after["collections"]["junctions"]["count"],
                     "pairs": after["total_pairs"]},
        "losses": losses
    }
