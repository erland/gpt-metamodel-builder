"""CORE-015: deterministic expansion of declared pairs to concrete element subtypes.

This is an opt-in analysis helper. It does not alter legacy endpoint rules or
infer pairs when allowed_type_pairs is absent.
"""
from __future__ import annotations


def effective_pairs(model: dict, relation_id: str) -> list[dict[str, str]]:
    elements = {e["id"]: e for e in model["elements"]}
    relations = {r["id"]: r for r in model["relationships"]}
    if relation_id not in relations:
        raise ValueError("Unknown relationship type: " + relation_id)
    relation = relations[relation_id]
    if "allowed_type_pairs" not in relation:
        raise ValueError("Pairwise profile not declared on relationship: " + relation_id)

    def ancestry(ident: str, stack: frozenset[str] = frozenset()) -> frozenset[str]:
        if ident not in elements:
            raise ValueError("Unknown element type: " + ident)
        if ident in stack:
            raise ValueError("Element inheritance cycle: " + ident)
        parents = elements[ident].get("extends", []) or []
        return frozenset([ident]).union(
            *(ancestry(parent, stack | {ident}) for parent in parents)
        )

    ancestors = {ident: ancestry(ident) for ident in elements}
    result: set[tuple[str, str]] = set()
    for pair in relation["allowed_type_pairs"]:
        source, target = pair["source"], pair["target"]
        if source not in elements or target not in elements:
            raise ValueError("Unknown pair endpoint")
        if source not in relation["source"]["types"] or target not in relation["target"]["types"]:
            raise ValueError("Pair outside declared endpoint types")
        sources = [key for key in elements if source in ancestors[key] and not elements[key].get("abstract", False)]
        targets = [key for key in elements if target in ancestors[key] and not elements[key].get("abstract", False)]
        result.update((left, right) for left in sources for right in targets)
    return [{"source": s, "target": t} for s, t in sorted(result)]
