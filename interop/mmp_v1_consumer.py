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
    return {"package_format_version": m["package_format_version"], "metamodel": m["metamodel"],
            "elements": [{"id": x["id"], "name": x["name"]} for x in elements],
            "relationships": [{"id": x["id"], "name": x["name"],
                               "source": x["source"]["types"], "target": x["target"]["types"]}
                              for x in relations],
            "data_types": props["data_types"], "enumerations": props["enumerations"],
            "properties": props["property_definitions"], "property_sets": props["property_sets"],
            "rules": rules}


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
