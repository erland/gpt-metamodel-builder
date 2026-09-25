#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

FILES = [
    "metamodel.yaml",
    "properties.yaml",
    "constraints.yaml",
    "viewpoints.yaml",
    "guidance.yaml",
    "notation.yaml",
    "provenance.yaml",
    "version.yaml",
]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected YAML mapping")
    return data


def card_min(card: str | None) -> int | None:
    if card is None or card == "*":
        return 0 if card == "*" else None
    if ".." in card:
        lo, _ = card.split("..", 1)
        return int(lo)
    return int(card)


class Report:
    def __init__(self, model_dir: Path):
        self.model_dir = str(model_dir)
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []

    def error(self, code: str, location: str, message: str):
        self.errors.append({"code": code, "location": location, "message": message})

    def warn(self, code: str, location: str, message: str):
        self.warnings.append({"code": code, "location": location, "message": message})

    def as_dict(self) -> dict[str, Any]:
        return {
            "validator": "metamodel-builder-semantic-v1",
            "model_dir": self.model_dir,
            "status": "fail" if self.errors else "pass",
            "summary": {"errors": len(self.errors), "warnings": len(self.warnings)},
            "errors": self.errors,
            "warnings": self.warnings,
        }


def duplicate_ids(items: list[dict[str, Any]], label: str, report: Report):
    seen: set[str] = set()
    for i, item in enumerate(items):
        ident = item.get("id")
        if ident in seen:
            report.error("duplicate_id", f"{label}[{i}].id", f"Duplicate id '{ident}' in {label}")
        seen.add(ident)


def find_cycles(nodes: dict[str, list[str]], label: str, report: Report):
    WHITE, GRAY, BLACK = 0, 1, 2
    state = {n: WHITE for n in nodes}
    stack: list[str] = []

    def visit(node: str):
        state[node] = GRAY
        stack.append(node)
        for parent in nodes.get(node, []):
            if parent not in nodes:
                continue
            if state[parent] == GRAY:
                start = stack.index(parent)
                cycle = stack[start:] + [parent]
                report.error("inheritance_cycle", label, " -> ".join(cycle))
            elif state[parent] == WHITE:
                visit(parent)
        stack.pop()
        state[node] = BLACK

    for node in nodes:
        if state[node] == WHITE:
            visit(node)


def normalize_expr(expr: str) -> str:
    return re.sub(r"\s+", " ", expr.strip().lower())


def opposite_expr(expr: str) -> str | None:
    e = normalize_expr(expr)
    m = re.fullmatch(r"property\(([^)]+)\) is not empty", e)
    if m:
        return f"property({m.group(1)}) is empty"
    m = re.fullmatch(r"property\(([^)]+)\) is empty", e)
    if m:
        return f"property({m.group(1)}) is not empty"
    m = re.fullmatch(r"property\(([^)]+)\) = (.+)", e)
    if m:
        return f"property({m.group(1)}) != {m.group(2)}"
    m = re.fullmatch(r"property\(([^)]+)\) != (.+)", e)
    if m:
        return f"property({m.group(1)}) = {m.group(2)}"
    return None


def validate(model_dir: Path) -> Report:
    report = Report(model_dir)
    missing = [name for name in FILES if not (model_dir / name).is_file()]
    if missing:
        for name in missing:
            report.error("missing_file", name, "Required canonical file is missing")
        return report

    docs = {name: load_yaml(model_dir / name) for name in FILES}
    mm = docs["metamodel.yaml"]
    props = docs["properties.yaml"]
    cons = docs["constraints.yaml"]
    views = docs["viewpoints.yaml"]
    guidance = docs["guidance.yaml"]
    notation = docs["notation.yaml"]
    provenance = docs["provenance.yaml"]
    version = docs["version.yaml"]

    collections = {
        "elements": mm.get("elements", []),
        "relationships": mm.get("relationships", []),
        "data_types": props.get("data_types", []),
        "enumerations": props.get("enumerations", []),
        "property_definitions": props.get("property_definitions", []),
        "property_sets": props.get("property_sets", []),
        "constraints": cons.get("constraints", []),
        "viewpoints": views.get("viewpoints", []),
        "styles": notation.get("styles", []),
        "sources": provenance.get("sources", []),
    }
    for label, items in collections.items():
        duplicate_ids(items, label, report)

    for ei, enum in enumerate(collections["enumerations"]):
        duplicate_ids(enum.get("values", []), f"enumerations[{ei}].values", report)

    ids = {k: {x.get("id") for x in v} for k, v in collections.items()}
    element_ids = ids["elements"]
    relationship_ids = ids["relationships"]
    property_ids = ids["property_definitions"]
    property_set_ids = ids["property_sets"]
    data_type_ids = ids["data_types"]
    enum_ids = ids["enumerations"]
    viewpoint_ids = ids["viewpoints"]
    source_ids = ids["sources"]

    # Avoid ambiguous model type identifiers.
    overlap = element_ids & relationship_ids
    for ident in sorted(overlap):
        report.error("ambiguous_type_id", "metamodel.yaml", f"Id '{ident}' is used by both an element and a relationship type")

    # Inheritance and references.
    elem_graph: dict[str, list[str]] = {}
    for i, item in enumerate(collections["elements"]):
        ident = item.get("id")
        parents = item.get("extends", []) or []
        elem_graph[ident] = parents
        for ref in parents:
            if ref not in element_ids:
                report.error("unknown_element_parent", f"elements[{i}].extends", f"Unknown element type '{ref}'")
        for ref in item.get("property_sets", []) or []:
            if ref not in property_set_ids:
                report.error("unknown_property_set", f"elements[{i}].property_sets", f"Unknown property set '{ref}'")
    find_cycles(elem_graph, "elements.extends", report)

    rel_graph: dict[str, list[str]] = {}
    for i, item in enumerate(collections["relationships"]):
        ident = item.get("id")
        parents = item.get("extends", []) or []
        rel_graph[ident] = parents
        for ref in parents:
            if ref not in relationship_ids:
                report.error("unknown_relationship_parent", f"relationships[{i}].extends", f"Unknown relationship type '{ref}'")
        for ref in item.get("property_sets", []) or []:
            if ref not in property_set_ids:
                report.error("unknown_property_set", f"relationships[{i}].property_sets", f"Unknown property set '{ref}'")
        for side in ("source", "target"):
            for ref in item.get(side, {}).get("types", []) or []:
                if ref not in element_ids:
                    report.error("unknown_endpoint_type", f"relationships[{i}].{side}.types", f"Unknown element type '{ref}'")
    find_cycles(rel_graph, "relationships.extends", report)

    # Property type and property set references.
    enum_values = {e["id"]: {v["id"] for v in e.get("values", [])} for e in collections["enumerations"]}
    for i, prop in enumerate(collections["property_definitions"]):
        typ = prop.get("type", {})
        if "data_type" in typ and typ["data_type"] not in data_type_ids:
            report.error("unknown_data_type", f"property_definitions[{i}].type", f"Unknown data type '{typ['data_type']}'")
        if "enumeration" in typ and typ["enumeration"] not in enum_ids:
            report.error("unknown_enumeration", f"property_definitions[{i}].type", f"Unknown enumeration '{typ['enumeration']}'")
        if prop.get("required") is True:
            minimum = card_min(prop.get("cardinality"))
            if minimum == 0:
                report.error("required_cardinality_conflict", f"property_definitions[{i}]", "required=true conflicts with cardinality that permits zero values")
        if "default" in prop and "enumeration" in typ and typ["enumeration"] in enum_values:
            if prop["default"] not in enum_values[typ["enumeration"]]:
                report.error("invalid_enum_default", f"property_definitions[{i}].default", f"Default '{prop['default']}' is not a member of enumeration '{typ['enumeration']}'")

    for i, pset in enumerate(collections["property_sets"]):
        for ref in pset.get("properties", []) or []:
            if ref not in property_ids:
                report.error("unknown_property", f"property_sets[{i}].properties", f"Unknown property '{ref}'")

    # Viewpoints and endpoint closure.
    rel_by_id = {r["id"]: r for r in collections["relationships"]}
    for i, view in enumerate(collections["viewpoints"]):
        allowed_elements = set(view.get("allowed_elements", []) or [])
        allowed_relationships = set(view.get("allowed_relationships", []) or [])
        for ref in allowed_elements:
            if ref not in element_ids:
                report.error("unknown_viewpoint_element", f"viewpoints[{i}].allowed_elements", f"Unknown element type '{ref}'")
        for ref in allowed_relationships:
            if ref not in relationship_ids:
                report.error("unknown_viewpoint_relationship", f"viewpoints[{i}].allowed_relationships", f"Unknown relationship type '{ref}'")
                continue
            rel = rel_by_id[ref]
            endpoint_types = set(rel.get("source", {}).get("types", [])) | set(rel.get("target", {}).get("types", []))
            missing_endpoint_types = endpoint_types - allowed_elements
            if missing_endpoint_types:
                report.error("viewpoint_relationship_endpoint_missing", f"viewpoints[{i}]", f"Relationship '{ref}' uses element types not allowed by viewpoint: {sorted(missing_endpoint_types)}")
        for ref in view.get("required_elements", []) or []:
            if ref not in element_ids:
                report.error("unknown_required_viewpoint_element", f"viewpoints[{i}].required_elements", f"Unknown element type '{ref}'")
            elif ref not in allowed_elements:
                report.error("required_element_not_allowed", f"viewpoints[{i}].required_elements", f"Required element '{ref}' is not listed in allowed_elements")


    # Modeling guidance references.
    for i, item in enumerate(guidance.get("elements", [])):
        ref=item.get("type")
        if ref not in element_ids:
            report.error("unknown_guidance_element", f"guidance.elements[{i}].type", f"Unknown element type '{ref}'")
        for rel in item.get("recommended_relationships", []) or []:
            if rel not in relationship_ids:
                report.error("unknown_guidance_relationship", f"guidance.elements[{i}].recommended_relationships", f"Unknown relationship type '{rel}'")
    for i, item in enumerate(guidance.get("relationships", [])):
        ref=item.get("type")
        if ref not in relationship_ids:
            report.error("unknown_guidance_relationship", f"guidance.relationships[{i}].type", f"Unknown relationship type '{ref}'")
    for i, item in enumerate(guidance.get("viewpoints", [])):
        ref=item.get("viewpoint")
        if ref not in viewpoint_ids:
            report.error("unknown_guidance_viewpoint", f"guidance.viewpoints[{i}].viewpoint", f"Unknown viewpoint '{ref}'")
    seen_guidance_ids=set()
    for group in ("patterns","anti_patterns"):
        for i, item in enumerate(guidance.get(group, [])):
            ident=item.get("id")
            if ident in seen_guidance_ids:
                report.error("duplicate_guidance_id", f"guidance.{group}[{i}].id", f"Duplicate guidance id '{ident}'")
            seen_guidance_ids.add(ident)
            for ref in item.get("elements", []) or []:
                if ref not in element_ids:
                    report.error("unknown_guidance_element", f"guidance.{group}[{i}].elements", f"Unknown element type '{ref}'")
            for ref in item.get("relationships", []) or []:
                if ref not in relationship_ids:
                    report.error("unknown_guidance_relationship", f"guidance.{group}[{i}].relationships", f"Unknown relationship type '{ref}'")

    # Notation references.
    for i, style in enumerate(collections["styles"]):
        applies = style.get("applies_to", {})
        kind, ref = applies.get("kind"), applies.get("type")
        valid = element_ids if kind == "element" else relationship_ids
        if ref not in valid:
            report.error("unknown_notation_target", f"styles[{i}].applies_to", f"Unknown {kind} type '{ref}'")
        for prop_ref in style.get("label", {}).get("show_properties", []) or []:
            if prop_ref not in property_ids:
                report.error("unknown_notation_property", f"styles[{i}].label.show_properties", f"Unknown property '{prop_ref}'")

    # Constraints and simple contradiction detection.
    type_sets = {
        "element": element_ids,
        "relationship": relationship_ids,
        "property": property_ids,
        "viewpoint": viewpoint_ids,
        "model": {mm.get("metamodel", {}).get("id")},
    }
    constraint_exprs: defaultdict[tuple[str, tuple[str, ...]], list[tuple[int, str, str]]] = defaultdict(list)
    for i, c in enumerate(collections["constraints"]):
        scope = c.get("applies_to", {})
        kind = scope.get("kind")
        types = scope.get("types", []) or []
        for ref in types:
            if ref not in type_sets.get(kind, set()):
                report.error("unknown_constraint_target", f"constraints[{i}].applies_to.types", f"Unknown {kind} target '{ref}'")
        rule = c.get("rule", {})
        if rule.get("language") == "declarative":
            expr = normalize_expr(rule.get("expression", ""))
            key = (kind, tuple(sorted(types)))
            constraint_exprs[key].append((i, c.get("id"), expr))
            # Declarative property() refs can be checked.
            for prop_ref in re.findall(r"property\(([^)]+)\)", expr):
                if prop_ref not in property_ids:
                    report.error("unknown_constraint_property", f"constraints[{i}].rule.expression", f"Unknown property '{prop_ref}'")
    for key, entries in constraint_exprs.items():
        expr_set = {e for _, _, e in entries}
        for i, cid, expr in entries:
            opp = opposite_expr(expr)
            if opp and opp in expr_set:
                report.error("contradictory_constraints", f"constraints[{i}]", f"Constraint '{cid}' conflicts with another constraint in the same scope: '{expr}' vs '{opp}'")

    # Provenance references.
    target_sets = {
        "element": element_ids,
        "relationship": relationship_ids,
        "property": property_ids,
        "viewpoint": viewpoint_ids,
    }
    for i, mapping in enumerate(provenance.get("mappings", [])):
        src = mapping.get("source", {}).get("source_id")
        if src not in source_ids:
            report.error("unknown_provenance_source", f"mappings[{i}].source.source_id", f"Unknown source '{src}'")
        target = mapping.get("target", {})
        kind, ident = target.get("kind"), target.get("id")
        if ident not in target_sets.get(kind, set()):
            report.error("unknown_provenance_target", f"mappings[{i}].target", f"Unknown {kind} target '{ident}'")

    # Version consistency.
    model_version = mm.get("metamodel", {}).get("version")
    current_version = version.get("version", {}).get("current")
    if model_version != current_version:
        report.error("version_mismatch", "version.current", f"metamodel.version '{model_version}' differs from version.current '{current_version}'")
    previous = version.get("version", {}).get("previous")
    level = version.get("version", {}).get("compatibility", {}).get("level")
    if previous and previous == current_version:
        report.error("previous_equals_current", "version.previous", "previous version must differ from current version")
    if level == "initial" and previous:
        report.warn("initial_with_previous", "version.compatibility.level", "Compatibility level is initial but a previous version is declared")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate semantic consistency of a canonical metamodel directory")
    parser.add_argument("model_dir", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    report = validate(args.model_dir)
    result = report.as_dict()
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
