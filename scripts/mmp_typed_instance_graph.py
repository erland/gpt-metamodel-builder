"""CORE-007 candidate: complete graph with element and relationship endpoints.

Instances of relationships are edge IDs. Junction topology remains unsupported.
Existing element-only graphs retain the legacy validate_graph implementation.
"""
from __future__ import annotations

from collections import Counter
from mmp_instance_cardinality import validate_incidence


def validate_typed_graph(model: dict, graph: dict) -> list[dict]:
    if graph.get("complete") is not True:
        raise ValueError("CORE-007 not_supported: complete=true required")
    if model.get("junctions") or graph.get("junctions"):
        raise ValueError("CORE-007 not_supported: junction topology")
    nodes, edges = graph.get("instances"), graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("CORE-007 invalid graph population")
    elements = {e["id"] for e in model["elements"]}
    relations = {r["id"]: r for r in model["relationships"]}
    node_types = {}
    for node in nodes:
        key, typ = node.get("id"), node.get("type")
        if not isinstance(key, str) or not key or key in node_types or typ not in elements:
            raise ValueError("CORE-007 invalid element instance")
        node_types[key] = typ
    edge_types = {}
    for edge in edges:
        key, typ = edge.get("id"), edge.get("relationship")
        if not isinstance(key, str) or not key or key in edge_types or key in node_types or typ not in relations:
            raise ValueError("CORE-007 invalid relationship instance")
        edge_types[key] = typ
    types = {"element": node_types, "relationship": edge_types}
    counts = Counter()
    for edge in edges:
        rel = relations[edge["relationship"]]
        for role in ("source", "target"):
            endpoint = edge.get(role)
            if not isinstance(endpoint, dict) or set(endpoint) != {"kind", "id"}:
                raise ValueError("CORE-007 typed endpoint requires kind and id")
            kind, ident = endpoint["kind"], endpoint["id"]
            if kind not in types or ident not in types[kind]:
                raise ValueError("CORE-007 dangling typed endpoint")
            allowed = {(r["kind"], r["id"]) for r in rel[role].get("typed_refs", [])}
            if not allowed:
                raise ValueError("CORE-007 not_supported: missing typed endpoint domain")
            if (kind, types[kind][ident]) not in allowed:
                raise ValueError("CORE-007 typed endpoint outside declared domain")
            counts[(rel["id"], role, kind, ident)] += 1

        if "allowed_typed_pairs" in rel:
            pair = tuple((edge[role]["kind"], types[edge[role]["kind"]][edge[role]["id"]])
                         for role in ("source", "target"))
            allowed_pairs = {tuple((p[role]["kind"], p[role]["id"]) for role in ("source", "target"))
                             for p in rel["allowed_typed_pairs"]}
            if pair not in allowed_pairs:
                raise ValueError("CORE-016 typed pair disallowed")

    # Zero incidence must be counted for every declared candidate endpoint instance.
    entries = []
    for rel in model["relationships"]:
        for role in ("source", "target"):
            domain = rel[role].get("typed_refs")
            if domain is None:
                raise ValueError("CORE-007 not_supported: typed domain absent")
            for ref in domain:
                kind, typ = ref["kind"], ref["id"]
                if kind not in types:
                    raise ValueError("CORE-007 not_supported: junction endpoint")
                for ident, actual_type in types[kind].items():
                    if actual_type == typ:
                        entries.append({"relationship": rel["id"], "role": role,
                                        "instance": kind + ":" + ident,
                                        "count": counts[(rel["id"], role, kind, ident)]})
    return validate_incidence(model, entries)
