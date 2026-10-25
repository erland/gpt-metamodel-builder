"""CORE-015/016 candidate: conservative inherited exact typed pair constraints.

Every parent contributes a restriction; none may lack an explicit/own inherited
contract. Exact type keys are used: no implicit subtype expansion.
"""
from __future__ import annotations


def effective_typed_pairs(model: dict, relationship_id: str) -> list[dict]:
    rels = {r["id"]: r for r in model["relationships"]}
    kinds = {
        "element": {x["id"] for x in model.get("elements", [])},
        "relationship": set(rels),
        "junction": {x["id"] for x in model.get("junctions", [])},
    }

    def pair_key(pair):
        if set(pair) != {"source", "target"}:
            raise ValueError("CORE-016 malformed typed pair")
        refs = []
        for side in ("source", "target"):
            ref = pair[side]
            if not isinstance(ref, dict) or set(ref) != {"kind", "id"}:
                raise ValueError("CORE-016 malformed typed reference")
            key = (ref["kind"], ref["id"])
            if key[0] not in kinds or key[1] not in kinds[key[0]]:
                raise ValueError("CORE-016 unknown typed endpoint type")
            refs.append(key)
        return tuple(refs)

    def constraints(ident, visiting=frozenset()):
        if ident not in rels:
            raise ValueError("CORE-016 unknown relationship parent")
        if ident in visiting:
            raise ValueError("CORE-016 relationship inheritance cycle")
        rel = rels[ident]
        result = []
        for parent in rel.get("extends", []) or []:
            inherited = constraints(parent, visiting | {ident})
            if not inherited:
                raise ValueError("CORE-016 not_supported: parent lacks typed pair contract")
            result.extend(inherited)
        if "allowed_typed_pairs" in rel:
            result.append({pair_key(p) for p in rel["allowed_typed_pairs"]})
        return result

    all_constraints = constraints(relationship_id)
    if not all_constraints:
        raise ValueError("CORE-016 not_supported: no inherited typed pair contract")
    pairs = set.intersection(*all_constraints)
    if not pairs:
        raise ValueError("CORE-016 empty inherited typed pair intersection")
    relation = rels[relationship_id]
    for side, index in (("source", 0), ("target", 1)):
        domain = relation[side].get("typed_refs")
        if not isinstance(domain, list):
            raise ValueError("CORE-016 not_supported: missing child typed endpoint domain")
        allowed = {(r["kind"], r["id"]) for r in domain}
        pairs = {p for p in pairs if p[index] in allowed}
    if not pairs:
        raise ValueError("CORE-016 no effective pairs within child typed domains")
    return [{"source": {"kind": p[0][0], "id": p[0][1]},
             "target": {"kind": p[1][0], "id": p[1][1]}}
            for p in sorted(pairs)]
