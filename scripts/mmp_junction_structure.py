"""Opt-in CORE-016 structural (not behavioural) junction checks."""
from __future__ import annotations
from collections import Counter

def validate_junction_structure(model: dict, graph: dict) -> list[dict]:
    if graph.get("complete") is not True:
        raise ValueError("CORE-016 not_supported: complete graph required")
    definitions = {j["id"]: j for j in model.get("junctions", [])}
    instances = graph.get("junctions")
    edges = graph.get("edges")
    if not isinstance(instances, list) or not isinstance(edges, list):
        raise ValueError("CORE-016 invalid junction graph")
    found = {}
    for instance in instances:
        ident, kind = instance.get("id"), instance.get("type")
        if not isinstance(ident, str) or not ident or ident in found or kind not in definitions:
            raise ValueError("CORE-016 invalid junction instance")
        found[ident] = kind
    counts = Counter()
    for edge in edges:
        for side, direction in (("source", "out"), ("target", "in")):
            endpoint = edge.get(side)
            if not isinstance(endpoint, dict):
                raise ValueError("CORE-016 invalid typed endpoint")
            if endpoint.get("kind") != "junction":
                continue
            ident = endpoint.get("id")
            if ident not in found:
                raise ValueError("CORE-016 dangling junction endpoint")
            counts[(ident, direction)] += 1
    problems = []
    for ident, typ in sorted(found.items()):
        definition = definitions[typ]
        operator = definition.get("operator")
        if operator not in ("and", "or"):
            raise ValueError("CORE-016 not_supported: junction operator must be declared as and/or")
        # Structural branching only: no token activation, reachability, or
        # evaluation of AND/OR behavioural truth values.
        incoming, outgoing = counts[(ident, "in")], counts[(ident, "out")]
        if incoming + outgoing < 2 or incoming == 0 or outgoing == 0:
            problems.append({"junction": ident, "operator": operator,
                             "incoming": incoming, "outgoing": outgoing,
                             "reason": "structural_branch_missing"})
    return problems
