"""CORE-007 experimental complete graph-to-incidence adapter.

Only element endpoints are supported in this stage. A complete graph declares
its whole instance population and relationship edge population explicitly.
"""
from __future__ import annotations

from collections import Counter
from mmp_instance_cardinality import validate_incidence


def validate_graph(model: dict, graph: dict) -> list[dict]:
    if graph.get("complete") is not True:
        raise ValueError("CORE-007 not_supported: instance graph must declare complete=true")
    nodes = graph.get("instances")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("CORE-007 invalid graph population")
    node_types = {}
    known_elements = {element["id"] for element in model["elements"]}
    rels = {rel["id"]: rel for rel in model["relationships"]}
    for node in nodes:
        ident, typ = node.get("id"), node.get("type")
        if not isinstance(ident, str) or not ident or ident in node_types or typ not in known_elements:
            raise ValueError("CORE-007 invalid or duplicate instance")
        node_types[ident] = typ
    counted = Counter()
    edge_ids = set()
    for edge in edges:
        ident, rel_id = edge.get("id"), edge.get("relationship")
        source, target = edge.get("source"), edge.get("target")
        if not isinstance(ident, str) or not ident or ident in edge_ids:
            raise ValueError("CORE-007 duplicate or invalid edge ID")
        edge_ids.add(ident)
        if rel_id not in rels or source not in node_types or target not in node_types:
            raise ValueError("CORE-007 dangling relation or endpoint reference")
        rel = rels[rel_id]
        if any("typed_refs" in rel[side] for side in ("source", "target")) or model.get("junctions"):
            raise ValueError("CORE-007 not_supported: typed endpoints and junctions require separate semantics")
        if node_types[source] not in rel["source"]["types"] or node_types[target] not in rel["target"]["types"]:
            raise ValueError("CORE-007 endpoint instance type outside declared domain")
        counted[(rel_id, "source", source)] += 1
        counted[(rel_id, "target", target)] += 1

    # Complete population: evaluate all matching endpoint instances, including zero edges.
    counts = []
    for rel in model["relationships"]:
        if any("typed_refs" in rel[side] for side in ("source", "target")) or model.get("junctions"):
            raise ValueError("CORE-007 not_supported: typed endpoints and junctions require separate semantics")
        for role in ("source", "target"):
            types = set(rel[role]["types"])
            for node_id, typ in node_types.items():
                if typ in types:
                    counts.append({"relationship": rel["id"], "role": role,
                                   "instance": node_id, "count": counted[(rel["id"], role, node_id)]})
    return validate_incidence(model, counts)
