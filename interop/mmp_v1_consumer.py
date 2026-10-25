#!/usr/bin/env python3
"""Independent MMP v1 read-only reference consumer.

Uses only documented MMP structures and standard parsing libraries; does not
import Metamodel Builder's exporter, importer or semantic validator.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

REQUIRED = ("metamodel", "properties", "constraints", "viewpoints", "notation", "provenance", "version")


def valid_path(s):
    return bool(s) and not s.startswith("/") and "\\" not in s and not re.match(r"^[a-zA-Z]:", s) and all(
        part not in ("", ".", "..") for part in s.split("/")
    ) and PurePosixPath(s).as_posix() == s


def read(source: Path):
    if source.is_dir():
        files = {}
        for p in source.rglob("*"):
            if p.is_symlink():
                raise ValueError("Symlinks forbidden")
            if p.is_file():
                name = p.relative_to(source).as_posix()
                if not valid_path(name):
                    raise ValueError("Unsafe path")
                files[name] = p.read_bytes()
    else:
        files = {}
        with zipfile.ZipFile(source) as z:
            for info in z.infolist():
                if not valid_path(info.filename) or info.is_dir() or info.filename in files:
                    raise ValueError("Invalid/duplicate ZIP entry")
                if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
                    raise ValueError("Symlinks forbidden")
                if info.file_size > 8_388_608 or info.file_size and (
                    info.compress_size == 0 or info.file_size / info.compress_size > 200
                ):
                    raise ValueError("Oversized/compression bomb member")
                files[info.filename] = z.read(info)
    if len(files) > 300 or sum(map(len, files.values())) > 33_554_432:
        raise ValueError("Package size limit exceeded")
    return files



def parse_cardinality(value: str):
    """Parse candidate Core cardinality semantics without changing MMP 1.0.0 admission."""
    if not isinstance(value, str):
        raise ValueError("Cardinality must be text")
    import re
    part = r"(?:0|[1-9][0-9]*)"
    if value == "*":
        return {"min": 0, "max": None}
    if re.fullmatch(part, value):
        n = int(value)
        return {"min": n, "max": n}
    match = re.fullmatch(rf"({part})[.]{{2}}({part}|[*])", value)
    if not match:
        raise ValueError("Invalid cardinality syntax")
    minimum = int(match.group(1))
    maximum = None if match.group(2) == "*" else int(match.group(2))
    if maximum is not None and minimum > maximum:
        raise ValueError("Inverted cardinality interval")
    return {"min": minimum, "max": maximum}


def required_profile(required: bool, cardinality: str | None):
    """Return accept or undecided; never silently settle conflicting 1.0.0 semantics."""
    if cardinality is None:
        return "accept"
    bounds = parse_cardinality(cardinality)
    if required is True and bounds["min"] == 0:
        return "undecided"
    return "accept"



def validate_default_value(type_name, value, *, values=None, cardinality=None):
    """Opt-in prospective Core value semantics; not used for 1.0.0 admission."""
    from datetime import date, datetime
    import math
    import re
    if cardinality is not None:
        bounds = parse_cardinality(cardinality)
        count = len(value) if isinstance(value, list) else 1
        if count < bounds["min"] or (bounds["max"] is not None and count > bounds["max"]):
            return False
    elif isinstance(value, list):
        return False
    items = value if isinstance(value, list) else [value]
    for item in items:
        if type_name in ("string", "identifier"):
            valid = isinstance(item, str) and (type_name != "identifier" or bool(item))
        elif type_name == "integer":
            valid = type(item) is int
        elif type_name == "decimal":
            valid = type(item) in (int, float) and math.isfinite(item)
        elif type_name == "boolean":
            valid = type(item) is bool
        elif type_name == "date":
            valid = isinstance(item, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", item) is not None
            if valid:
                try: date.fromisoformat(item)
                except ValueError: valid = False
        elif type_name == "datetime":
            valid = isinstance(item, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})", item) is not None
            if valid:
                try: datetime.fromisoformat(item.replace("Z", "+00:00"))
                except ValueError: valid = False
        elif type_name == "uri":
            valid = isinstance(item, str) and bool(re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", item)) and not any(c.isspace() for c in item)
        elif type_name == "enumeration":
            valid = isinstance(item, str) and isinstance(values, list) and item in values
        else:
            valid = False
        if not valid:
            return False
    return True



def relationship_semantics(elements, relationships):
    """Opt-in role/subtype interpretation. Does not change 1.0 admission."""
    by_element = {x["id"]: x for x in elements}
    by_relation = {x["id"]: x for x in relationships}
    def descendants(element, ancestor):
        seen = set()
        todo = [element]
        while todo:
            current = todo.pop()
            if current == ancestor:
                return True
            if current in seen or current not in by_element:
                continue
            seen.add(current)
            todo.extend(by_element[current].get("extends", []))
        return False
    result = {}
    for identifier, rel in sorted(by_relation.items()):
        result[identifier] = {
            "directed": rel.get("directed", True),
            "source_types": sorted(rel["source"]["types"]),
            "target_types": sorted(rel["target"]["types"]),
            "source_navigable": rel["source"].get("navigable"),
            "target_navigable": rel["target"].get("navigable"),
        }
    def allowed(relation, source, target):
        if relation not in by_relation or source not in by_element or target not in by_element:
            return False
        spec = by_relation[relation]
        return (any(descendants(source, x) for x in spec["source"]["types"])
                and any(descendants(target, x) for x in spec["target"]["types"]))
    return result, allowed



def classify_model_change(before, after):
    """Conservative, opt-in semantic diff; uncertainty is never compatible."""
    if before.get("namespace") != after.get("namespace"):
        return "breaking"
    uncertain = False
    for collection in ("elements", "relationships"):
        old = {x["id"]: x for x in before.get(collection, [])}
        new = {x["id"]: x for x in after.get(collection, [])}
        if old.keys() - new.keys():
            return "breaking"
        for identifier in old.keys() & new.keys():
            a = {k: v for k, v in old[identifier].items() if k not in ("name", "description")}
            b = {k: v for k, v in new[identifier].items() if k not in ("name", "description")}
            if a != b:
                uncertain = True
    return "needs_review" if uncertain else "compatible"


def extension_support(extensions, recognized, critical):
    """External criticality policy: 1.0.0 itself does not declare criticality."""
    if not isinstance(extensions, dict):
        raise ValueError("Invalid extensions")
    unknown = set(extensions) - set(recognized)
    if unknown & set(critical):
        return "not_supported"
    return "preserved_uninterpreted" if unknown else "supported"



def relation_inheritance_profile(elements, relations):
    """Opt-in candidate narrowing rules, never invoked by MMP 1.0.0 admission."""
    by_element = {x["id"]: x for x in elements}
    by_relation = {x["id"]: x for x in relations}
    def subtype(actual, parent):
        if actual == parent:
            return True
        return any(subtype(p, parent) for p in by_element.get(actual, {}).get("extends", []))
    def bounds(text):
        return parse_cardinality(text)
    for rel in relations:
        for end in ("source", "target"):
            if "cardinality" in rel[end]:
                try: bounds(rel[end]["cardinality"])
                except ValueError: return "invalid"
    for rel in relations:
        parents = rel.get("extends", [])
        if len(parents) > 1:
            return "needs_review"
        for parent_id in parents:
            parent = by_relation.get(parent_id)
            if parent is None:
                return "invalid"
            if rel.get("directed", True) != parent.get("directed", True):
                return "breaking"
            for end in ("source", "target"):
                new_types = rel[end]["types"]
                allowed = parent[end]["types"]
                if not all(any(subtype(t, p) for p in allowed) for t in new_types):
                    return "breaking"
                old_card, new_card = parent[end].get("cardinality"), rel[end].get("cardinality")
                if (old_card is None) != (new_card is None):
                    return "needs_review"
                if old_card is not None:
                    old, new = bounds(old_card), bounds(new_card)
                    if new["min"] < old["min"] or (old["max"] is not None and (new["max"] is None or new["max"] > old["max"])):
                        return "breaking"
    return "compatible"



def required_minimum_policy(required, cardinality):
    """Opt-in Core candidate: required raises effective minimum to one."""
    try:
        bounds = parse_cardinality(cardinality) if cardinality is not None else {"min": 0, "max": None}
    except ValueError:
        return {"status": "invalid", "reason": "invalid_cardinality"}
    minimum = max(bounds["min"], 1 if required else 0)
    maximum = bounds["max"]
    if maximum is not None and minimum > maximum:
        return {"status": "invalid", "reason": "empty_upper_bound"}
    return {"status": "valid", "effective_min": minimum, "effective_max": maximum}



def canonical_value(kind, value):
    """Proposed opt-in canonical text profile, independent of MMP 1.0 admission."""
    import re
    from decimal import Decimal
    from datetime import datetime, date, timezone
    from urllib.parse import urlsplit, urlunsplit
    if kind == "integer":
        if not re.fullmatch(r"(?:0|-?[1-9][0-9]*)", value):
            return {"error": "invalid_integer"}
        if abs(int(value)) > 9007199254740991:
            return {"error": "unsafe_integer"}
        return {"expected": value}
    if kind == "decimal":
        if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:[.][0-9]+)?", value):
            return {"error": "invalid_decimal"}
        d = Decimal(value)
        normalized = format(d, "f").rstrip("0").rstrip(".") if "." in format(d, "f") else format(d, "f")
        return {"expected": "0" if d == 0 else normalized}
    if kind == "date":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            return {"error": "invalid_date"}
        try: date.fromisoformat(value)
        except ValueError: return {"error": "invalid_date"}
        return {"expected": value}
    if kind == "datetime":
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})", value):
            return {"error": "invalid_datetime"}
        try:
            d = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if d.utcoffset() is None: raise ValueError()
            result = d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            return {"expected": result}
        except (ValueError, OverflowError): return {"error": "invalid_datetime"}
    if kind == "uri":
        if any(ch.isspace() for ch in value):
            return {"error": "invalid_uri"}
        try:
            parsed = urlsplit(value)
            if parsed.scheme.lower() not in ("http", "https") or not parsed.hostname:
                return {"error": "invalid_uri"}
            if parsed.username or parsed.password:
                return {"error": "invalid_uri"}
            host = parsed.hostname.lower()
            port = parsed.port
            netloc = host + ((":" + str(port)) if port is not None else "")
            return {"expected": urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, parsed.fragment))}
        except ValueError:
            return {"error": "invalid_uri"}
    return {"error": "unsupported_type"}



def negotiate_extensions(requirement, consumer):
    """Opt-in external negotiation; 1.0.0 manifests are unchanged."""
    supported = {(item["id"], version) for item in consumer for version in item["versions"]}
    missing = sorted(f'{item["id"]}@{item["version"]}' for item in requirement["required"] if (item["id"],item["version"]) not in supported)
    optional = sorted(f'{item["id"]}@{item["version"]}' for item in requirement["optional"] if (item["id"],item["version"]) not in supported)
    return {"status": "not_supported" if missing else "partial" if optional else "supported",
            "missing_required": missing, "ignored_optional": optional}


def effective_properties(elements, relationships, property_sets, property_definitions):
    """Deterministic ID-based transitive property union (Core draft)."""
    known_sets = {x["id"]: x["properties"] for x in property_sets}
    known_properties = {x["id"] for x in property_definitions}
    result = {}
    for label, types in (("elements", elements), ("relationships", relationships)):
        by_id = {item["id"]: item for item in types}
        cache = {}
        visiting = set()
        def resolve(identifier):
            if identifier in cache:
                return cache[identifier]
            if identifier in visiting:
                raise ValueError("Inheritance cycle")
            if identifier not in by_id:
                raise ValueError("Unknown inherited type")
            visiting.add(identifier)
            item = by_id[identifier]
            sets = set(item.get("property_sets", []) or [])
            for parent in item.get("extends", []) or []:
                sets.update(resolve(parent)["property_sets"])
            visiting.remove(identifier)
            if not sets <= known_sets.keys():
                raise ValueError("Unknown property set")
            props = set()
            for set_id in sets:
                props.update(known_sets[set_id])
            if not props <= known_properties:
                raise ValueError("Unknown property definition")
            cache[identifier] = {"property_sets": sorted(sets), "properties": sorted(props)}
            return cache[identifier]
        result[label] = {identifier: resolve(identifier) for identifier in sorted(by_id)}
    return result

def consume(source: Path):
    files = read(source)
    m = yaml.safe_load(files["manifest.yaml"])
    if m.get("package_format") != "mmp" or m.get("package_format_version") != "1.0.0":
        raise ValueError("Unsupported MMP format")
    if not isinstance(m, dict) or not isinstance(m.get("files"), list) or not isinstance(m.get("entrypoints"), dict):
        raise ValueError("Invalid MMP manifest structure")
    declared = m["files"]
    names = [item["path"] for item in declared]
    if len(names) != len(set(names)) or set(names) != set(files) - {"manifest.yaml"}:
        raise ValueError("Invalid manifest inventory")
    for item in declared:
        name = item["path"]
        if not valid_path(name) or name not in files or hashlib.sha256(files[name]).hexdigest() != item["sha256"]:
            raise ValueError(f"Invalid path or SHA-256: {name}")
    schema_by_id = {}
    for name, content in files.items():
        if name.startswith("schemas/") and name.endswith(".schema.json"):
            schema = json.loads(content)
            Draft202012Validator.check_schema(schema)
            schema_by_id[schema["$id"]] = schema
    # Reject unresolved remote schema references before invoking a resolver.
    for name, schema in ((n, json.loads(raw)) for n, raw in files.items() if n.startswith("schemas/") and n.endswith(".schema.json")):
        def check_refs(node):
            if isinstance(node, dict):
                ref = node.get("$ref")
                if isinstance(ref, str) and not ref.startswith("#"):
                    target = ref.split("#", 1)[0]
                    if target and (target.startswith("https:") or target.startswith("http:") or target.startswith("/") or "/" in target or ".." in target or f"schemas/{target}" not in files):
                        raise ValueError(f"Nonlocal or unresolved schema reference: {ref}")
                for value in node.values(): check_refs(value)
            elif isinstance(node, list):
                for value in node: check_refs(value)
        check_refs(schema)
    registry = Registry()
    for ident, schema in schema_by_id.items():
        registry = registry.with_resource(ident, Resource.from_contents(schema))
    docs = {}
    for key in REQUIRED:
        name = m["entrypoints"][key]
        if name not in files or not valid_path(name):
            raise ValueError(f"Missing canonical entrypoint: {key}")
        schema_name = f"schemas/{key}.schema.json"
        if schema_name not in files:
            raise ValueError(f"Missing schema: {schema_name}")
        schema = json.loads(files[schema_name])
        doc = yaml.safe_load(files[name])
        Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).validate(doc)
        docs[key] = doc
    meta = docs["metamodel"]["metamodel"]
    if (meta["id"], meta["version"], meta.get("namespace")) != (
        m["metamodel"]["id"], m["metamodel"]["version"], m["metamodel"]["namespace"]
    ) or docs["version"]["version"]["current"] != meta["version"]:
        raise ValueError("Metamodel identity mismatch")
    elements = docs["metamodel"]["elements"]
    relations = docs["metamodel"]["relationships"]
    props = docs["properties"]
    ids = {x["id"] for x in elements}
    for r in relations:
        for end in ("source", "target"):
            for value in r[end]["types"]:
                if value not in ids:
                    raise ValueError(f"Unknown relationship endpoint: {value}")
    # Independently enforce essential cross-document invariants.
    def unique(items, label):
        identifiers = [item["id"] for item in items]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError(f"Duplicate identifier in {label}")
        return set(identifiers)

    element_ids = unique(elements, "elements")
    relation_ids = unique(relations, "relationships")
    if element_ids & relation_ids:
        raise ValueError("Element/relationship type ID collision")
    property_ids = unique(props["property_definitions"], "property_definitions")
    set_ids = unique(props["property_sets"], "property_sets")
    data_type_ids = unique(props["data_types"], "data_types")
    enum_ids = unique(props["enumerations"], "enumerations")
    for collection, available, label in (
        (elements, element_ids, "elements"), (relations, relation_ids, "relationships")
    ):
        graph = {item["id"]: item.get("extends", []) or [] for item in collection}
        visiting, visited = set(), set()
        def visit(node):
            if node in visiting:
                raise ValueError(f"Inheritance cycle in {label}: {node}")
            if node in visited:
                return
            visiting.add(node)
            for parent in graph[node]:
                if parent not in available:
                    raise ValueError(f"Unknown inherited type: {parent}")
                visit(parent)
            visiting.remove(node)
            visited.add(node)
        for node in graph:
            visit(node)
        for item in collection:
            for ref in item.get("property_sets", []) or []:
                if ref not in set_ids:
                    raise ValueError(f"Unknown property set: {ref}")
    for item in props["property_sets"]:
        for ref in item["properties"]:
            if ref not in property_ids:
                raise ValueError(f"Unknown property definition: {ref}")
    for item in props["property_definitions"]:
        datatype = item["type"]
        if datatype.get("data_type") and datatype["data_type"] not in data_type_ids:
            raise ValueError(f"Unknown data type: {datatype['data_type']}")
        if datatype.get("enumeration") and datatype["enumeration"] not in enum_ids:
            raise ValueError(f"Unknown enumeration: {datatype['enumeration']}")
    for item in props["enumerations"]:
        unique(item["values"], f"enumeration {item['id']} values")
    for key, collection in (("constraints", docs["constraints"].get("constraints", [])),
                            ("viewpoints", docs["viewpoints"].get("viewpoints", []))):
        unique(collection, key)
    known_languages = {"declarative"}
    rules = [{"id": c["id"], "language": c.get("language"),
              "evaluation": "not_supported" if c.get("language") not in known_languages else "not_supported"}
             for c in docs["constraints"].get("constraints", [])]
    effective = effective_properties(elements, relations, props["property_sets"], props["property_definitions"])
    return {"effective_properties": effective, "package_format_version": m["package_format_version"], "metamodel": m["metamodel"],
            "elements": [{"id": x["id"], "name": x["name"]} for x in elements],
            "relationships": [{"id": x["id"], "name": x["name"],
                               "source": x["source"]["types"], "target": x["target"]["types"]}
                              for x in relations],
            "data_types": props["data_types"], "enumerations": props["enumerations"],
            "properties": props["property_definitions"], "property_sets": props["property_sets"],
            "rules": rules}



def strict_core_candidate(source: Path):
    """Explicit opt-in package-level candidate checks after legacy admission."""
    base = consume(source)
    files = read(source)
    model = yaml.safe_load(files["canonical/metamodel.yaml"])
    props = yaml.safe_load(files["canonical/properties.yaml"])
    diagnostics = []
    for relation in model["relationships"]:
        for end in ("source", "target"):
            value = relation[end].get("cardinality")
            if value is not None:
                try:
                    parse_cardinality(value)
                except ValueError:
                    diagnostics.append(f"invalid_endpoint_cardinality:{relation['id']}:{end}")
    for prop in props["property_definitions"]:
        value = prop.get("cardinality")
        if value is not None:
            try:
                parse_cardinality(value)
            except ValueError:
                diagnostics.append(f"invalid_property_cardinality:{prop['id']}")
                continue
        outcome = required_minimum_policy(prop.get("required", False), value)
        if outcome["status"] == "invalid":
            diagnostics.append(f"required_cardinality:{prop['id']}:{outcome['reason']}")
    return {"status": "reject" if diagnostics else "accept", "diagnostics": sorted(diagnostics),
            "effective_properties": base["effective_properties"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("package", type=Path)
    a = ap.parse_args()
    print(json.dumps(consume(a.package), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(f"MMP reference consumer: {ex}", file=sys.stderr)
        sys.exit(1)
