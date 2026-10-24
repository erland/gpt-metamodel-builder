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
    declared = m["files"]
    names = [item["path"] for item in declared]
    if len(names) != len(set(names)) or set(names) != set(files) - {"manifest.yaml"}:
        raise ValueError("Invalid manifest inventory")
    for item in declared:
        name = item["path"]
        if not valid_path(name) or hashlib.sha256(files[name]).hexdigest() != item["sha256"]:
            raise ValueError(f"Invalid path or SHA-256: {name}")
    schema_by_id = {}
    for name, content in files.items():
        if name.startswith("schemas/") and name.endswith(".schema.json"):
            schema = json.loads(content)
            Draft202012Validator.check_schema(schema)
            schema_by_id[schema["$id"]] = schema
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
