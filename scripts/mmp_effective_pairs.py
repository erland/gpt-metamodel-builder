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
    # A relation with no explicit pairs and no pairwise parents is legacy, not a profile.
    def inherited_constraints(ident: str, visiting: frozenset[str] = frozenset()) -> list[set[tuple[str, str]]]:
        if ident not in relations:
            raise ValueError("Unknown relationship parent: " + ident)
        if ident in visiting:
            raise ValueError("Relationship inheritance cycle: " + ident)
        item = relations[ident]
        constraints: list[set[tuple[str, str]]] = []
        for parent in item.get("extends", []) or []:
            parent_constraints = inherited_constraints(parent, visiting | {ident})
            if not parent_constraints:
                raise ValueError("CORE-015 not_supported: inherited relationship lacks explicit pairwise contract: " + parent)
            constraints.extend(parent_constraints)
        if "allowed_type_pairs" in item:
            constraints.append(set((pair["source"], pair["target"]) for pair in item["allowed_type_pairs"]))
        return constraints

    constraints = inherited_constraints(relation_id)
    if not constraints:
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
    def expand(pairs: set[tuple[str, str]]) -> set[tuple[str, str]]:
        result: set[tuple[str, str]] = set()
        for source, target in pairs:
            if source not in elements or target not in elements:
                raise ValueError("Unknown pair endpoint")
            sources = [key for key in elements if source in ancestors[key] and not elements[key].get("abstract", False)]
            targets = [key for key in elements if target in ancestors[key] and not elements[key].get("abstract", False)]
            result.update((left, right) for left in sources for right in targets)
        return result

    # Every parent restricts the child; multiple parents are intersected.
    result = set.intersection(*(expand(pairs) for pairs in constraints))
    # A child may narrow inherited pairs, never silently widen them.
    if not result:
        raise ValueError("CORE-015 empty effective pair intersection: " + relation_id)
    allowed_sources = set(relation["source"]["types"])
    allowed_targets = set(relation["target"]["types"])
    result = {(source, target) for source, target in result
              if ancestors[source] & allowed_sources and ancestors[target] & allowed_targets}
    if not result:
        raise ValueError("CORE-015 no effective pairs within child endpoint types: " + relation_id)
    return [{"source": s, "target": t} for s, t in sorted(result)]
