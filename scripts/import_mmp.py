#!/usr/bin/env python3
"""Secure MMP v1 inspect, validate and import (never executes package contents)."""
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

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" if (ROOT / "schemas").is_dir() else ROOT / "assets" / "schemas"
GUIDANCE = ROOT / "templates/metamodel/guidance.yaml" if (ROOT / "templates/metamodel/guidance.yaml").is_file() else ROOT / "assets/metamodel/guidance.yaml"
REQUIRED = ("metamodel", "properties", "constraints", "viewpoints", "notation", "provenance", "version")
LIMIT_FILES = 300
LIMIT_TOTAL = 32 * 1024 * 1024
LIMIT_SINGLE = 8 * 1024 * 1024
LIMIT_RATIO = 200


def safe_path(name: str) -> bool:
    p = PurePosixPath(name)
    return bool(name) and not name.startswith("/") and "\\" not in name and not name.endswith("/") and all(
        part not in ("", ".", "..") for part in name.split("/")
    ) and not re.match(r"^[A-Za-z]:", name) and str(p) == name


def read_package(source: Path) -> dict[str, bytes]:
    if source.is_dir():
        paths = [p for p in source.rglob("*") if p.is_file() or p.is_symlink()]
        if len(paths) > LIMIT_FILES:
            raise ValueError("Too many package files")
        result = {}
        total = 0
        for path in paths:
            rel = path.relative_to(source).as_posix()
            if not safe_path(rel) or path.is_symlink():
                raise ValueError(f"Unsafe package path: {rel}")
            if path.stat().st_size > LIMIT_SINGLE:
                raise ValueError(f"Oversized file: {rel}")
            total += path.stat().st_size
            if total > LIMIT_TOTAL:
                raise ValueError("Package exceeds size limit")
            result[rel] = path.read_bytes()
        return result
    if not source.is_file() or not zipfile.is_zipfile(source):
        raise ValueError("Expected MMP directory or ZIP")
    result = {}
    total = 0
    with zipfile.ZipFile(source) as z:
        infos = z.infolist()
        if len(infos) > LIMIT_FILES:
            raise ValueError("Too many archive entries")
        for info in infos:
            name = info.filename
            if not safe_path(name) or info.is_dir():
                raise ValueError(f"Unsafe or unexpected ZIP entry: {name}")
            if name in result:
                raise ValueError(f"Duplicate ZIP entry: {name}")
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise ValueError(f"ZIP symlink forbidden: {name}")
            if info.file_size > LIMIT_SINGLE:
                raise ValueError(f"Oversized ZIP member: {name}")
            if info.file_size and (info.compress_size == 0 or info.file_size / info.compress_size > LIMIT_RATIO):
                raise ValueError(f"Compression ratio limit exceeded: {name}")
            total += info.file_size
            if total > LIMIT_TOTAL:
                raise ValueError("Archive exceeds size limit")
            data = z.read(info)
            if len(data) != info.file_size:
                raise ValueError(f"Incorrect decompressed length: {name}")
            result[name] = data
    return result


def load_manifest(files: dict[str, bytes]) -> dict:
    if "manifest.yaml" not in files:
        raise ValueError("manifest.yaml missing")
    manifest = yaml.safe_load(files["manifest.yaml"])
    schema = json.loads((SCHEMAS / "mmp-manifest-v1.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    if manifest["package_format_version"] != "1.0.0":
        raise ValueError("Unsupported MMP minor or major version")
    entries = manifest["entrypoints"]
    for key in REQUIRED:
        if key not in entries:
            raise ValueError(f"Missing entrypoint: {key}")
    listed = [item["path"] for item in manifest["files"]]
    if len(set(listed)) != len(listed):
        raise ValueError("Duplicate paths in manifest")
    if set(listed) != set(files) - {"manifest.yaml"}:
        raise ValueError("Undeclared or missing package files")
    for item in manifest["files"]:
        path = item["path"]
        if not safe_path(path):
            raise ValueError(f"Unsafe manifest path: {path}")
        if hashlib.sha256(files[path]).hexdigest() != item["sha256"]:
            raise ValueError(f"SHA-256 mismatch: {path}")
        if item["role"] == "canonical" and (not path.startswith("canonical/") or not path.endswith(".yaml")):
            raise ValueError(f"Invalid canonical location: {path}")
        if item["role"] == "schema" and (not path.startswith("schemas/") or not path.endswith(".schema.json")):
            raise ValueError(f"Invalid schema location: {path}")
        if item["role"] == "documentation" and not path.startswith("documentation/"):
            raise ValueError(f"Invalid documentation location: {path}")
    for key, path in entries.items():
        if not safe_path(path) or path not in files:
            raise ValueError(f"Invalid canonical entrypoint {key}: {path}")
        if next(item for item in manifest["files"] if item["path"] == path)["role"] != "canonical":
            raise ValueError(f"Entrypoint must be canonical: {path}")
    return manifest


def validate_contents(files: dict[str, bytes], manifest: dict) -> dict:
    schemas = {}
    for name, payload in files.items():
        if name.startswith("schemas/"):
            schema = json.loads(payload)
            Draft202012Validator.check_schema(schema)
            if not isinstance(schema.get("$id"), str):
                raise ValueError(f"Schema lacks $id: {name}")
            if schema["$id"] in schemas:
                raise ValueError(f"Duplicate schema $id: {schema['$id']}")
            schemas[schema["$id"]] = schema
    registry = Registry()
    for uri, schema in schemas.items():
        registry = registry.with_resource(uri, Resource.from_contents(schema))
    documents = {}
    for key, path in manifest["entrypoints"].items():
        schema_path = f"schemas/{key}.schema.json"
        if schema_path not in files:
            raise ValueError(f"Missing offline schema: {schema_path}")
        schema = json.loads(files[schema_path])
        # Fail closed on references outside the package; no remote retrieval.
        def references(value):
            if isinstance(value, dict):
                if "$ref" in value and not value["$ref"].startswith("#"):
                    target = value["$ref"].split("#")[0]
                    if target and f"schemas/{target}" not in files:
                        raise ValueError(f"External/unresolved schema $ref: {value['$ref']}")
                for item in value.values():
                    references(item)
            elif isinstance(value, list):
                for item in value:
                    references(item)
        references(schema)
        doc = yaml.safe_load(files[path])
        errors = list(Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()).iter_errors(doc))
        if errors:
            raise ValueError(f"{key}: schema error: {errors[0].message}")
        documents[key] = doc
    mm = documents["metamodel"]["metamodel"]
    version = documents["version"]["version"]["current"]
    ident = manifest["metamodel"]
    if (mm["id"], mm["version"], version) != (ident["id"], ident["version"], ident["version"]):
        raise ValueError("Metamodel identity/version mismatch")
    if mm.get("namespace") != ident["namespace"]:
        raise ValueError("Metamodel namespace mismatch")
    # Canonical semantic checks must use the actual validator, not a replacement.
    from validate_semantics import validate as validate_semantics
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        model_dir = Path(td)
        for key, path in manifest["entrypoints"].items():
            (model_dir / f"{key}.yaml").write_bytes(files[path])
        if "guidance" not in manifest["entrypoints"]:
            template = GUIDANCE
            if not template.is_file():
                raise ValueError("Missing local guidance template for canonical validator")
            (model_dir / "guidance.yaml").write_bytes(template.read_bytes())
        report = validate_semantics(model_dir)
        if report.errors:
            raise ValueError(f"Canonical semantic validation failed: {report.errors[0].message if hasattr(report.errors[0], 'message') else report.errors[0]}")
    return {"elements": len(documents["metamodel"].get("elements", [])),
            "relationships": len(documents["metamodel"].get("relationships", [])),
            "properties": len(documents["properties"].get("property_definitions", []))}


def execute(source: Path, mode: str, destination: Path | None = None) -> dict:
    files = read_package(source)
    manifest = load_manifest(files)
    result = {"status": "pass", "mode": mode,
              "metamodel": manifest["metamodel"],
              "package_format_version": manifest["package_format_version"],
              "verified_sha256_files": len(manifest["files"])}
    if mode == "inspect":
        return result
    result["summary"] = validate_contents(files, manifest)
    if mode == "import":
        if destination is None:
            raise ValueError("--output is required for import")
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing workspace: {destination}")
        destination.mkdir(parents=True)
        try:
            for key, path in manifest["entrypoints"].items():
                (destination / f"{key}.yaml").write_bytes(files[path])
            if "guidance" not in manifest["entrypoints"]:
                (destination / "guidance.yaml").write_bytes(
                    (GUIDANCE).read_bytes())
        except Exception:
            import shutil
            shutil.rmtree(destination)
            raise
        result["imported_to"] = str(destination)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=("inspect", "validate", "import"))
    ap.add_argument("package", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    print(json.dumps(execute(args.package, args.mode, args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"MMP {sys.argv[1] if len(sys.argv)>1 else 'operation'} failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
