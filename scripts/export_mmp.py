#!/usr/bin/env python3
"""Export canonical YAML as a portable, checksummed MMP v1 directory or ZIP."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import yaml
from safe_yaml import safe_load
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas" if (ROOT / "schemas").is_dir() else ROOT / "assets"
CORE = ("metamodel", "properties", "constraints", "viewpoints",
        "notation", "provenance", "version")
ALL = (*CORE, "guidance")
SCHEMA_SUFFIX = ".schema.json"
ZIP_DATE = (1980, 1, 1, 0, 0, 0)


def timestamp() -> str:
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    moment = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch is not None else datetime.now(timezone.utc)
    return moment.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def collect(model_dir: Path, schema_dir: Path) -> dict[str, bytes]:
    result = {}
    for name in CORE:
        file = model_dir / (name + ".yaml")
        if not file.is_file():
            raise ValueError(f"Missing mandatory canonical file: {file}")
        result[f"canonical/{file.name}"] = file.read_bytes()
    if (model_dir / "guidance.yaml").is_file():
        result["canonical/guidance.yaml"] = (model_dir / "guidance.yaml").read_bytes()
    for name in [*ALL, "common-definitions"]:
        if name == "guidance" and "canonical/guidance.yaml" not in result:
            continue
        file = schema_dir / (name + SCHEMA_SUFFIX)
        if not file.is_file():
            raise ValueError(f"Missing offline schema: {file}")
        result[f"schemas/{file.name}"] = file.read_bytes()
    # Optional candidate profile is a separate, checksummed package document.
    profile = model_dir / "profiles" / "junction-structure.json"
    if profile.is_file():
        result["documentation/junction-structure.json"] = profile.read_bytes()
        schema = schema_dir / "mmp-junction-structure-profile.schema.json"
        result["schemas/mmp-junction-structure-profile.schema.json"] = schema.read_bytes()
    presence = model_dir / "profiles" / "required-default-presence.json"
    if presence.is_file():
        result["documentation/required-default-presence.json"] = presence.read_bytes()
        result["schemas/mmp-required-default-presence-profile.schema.json"] = (schema_dir / "mmp-required-default-presence-profile.schema.json").read_bytes()
    # Canonical schemas must be closed over their local schema dependencies.
    queue = [p for p in result if p.startswith("schemas/")]
    visited = set()
    while queue:
        key = queue.pop()
        if key in visited:
            continue
        visited.add(key)
        schema = json.loads(result[key])
        def walk(value):
            if isinstance(value, dict):
                ref = value.get("$ref")
                if isinstance(ref, str) and not ref.startswith("#"):
                    target = ref.split("#", 1)[0]
                    if "://" in target or target.startswith("/") or "/" in target or ".." in target:
                        raise ValueError(f"Nonlocal schema reference: {ref}")
                    if target:
                        name = f"schemas/{target}"
                        if name not in result:
                            source = schema_dir / target
                            if not source.is_file():
                                raise ValueError(f"Unresolved schema reference: {ref}")
                            result[name] = source.read_bytes()
                        queue.append(name)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(schema)
    return result


def export(model_dir: Path, output: Path, producer_version: str,
           *, schema_dir: Path = SCHEMAS, as_directory: bool = False,
           skip_validation: bool = False, candidate_1_1: bool = True) -> Path:
    model_dir = model_dir.resolve()
    contents = collect(model_dir, schema_dir.resolve())
    model_doc = safe_load(contents["canonical/metamodel.yaml"])
    model = model_doc["metamodel"]
    # CORE-015 is canonical-only until package consumers implement full pairwise semantics.
    # Never silently export pairwise rules into either MMP 1.0 or experimental 1.1.
    # CORE-016 remains canonical-only: older consumers cannot enforce typed endpoints.
    # Typed exact pairs need their own negotiated semantics; block until consumers support them.
    has_typed_pairs = any("allowed_typed_pairs" in rel for rel in model_doc["relationships"])
    if has_typed_pairs and not candidate_1_1:
        raise ValueError("CORE-016 not_supported: typed exact pairs require MMP 1.1 candidate")
    if has_typed_pairs and {"id": "mmp-typed-pairs", "version": "1.0.0"} not in model.get("extensions", {}).get("mmp_required_capabilities", []):
        raise ValueError("CORE-016 requires explicit mmp-typed-pairs@1.0.0 capability")
    has_typed = bool(model_doc.get("junctions")) or any(
        "typed_refs" in rel.get(side, {})
        for rel in model_doc["relationships"] for side in ("source", "target")
    )
    if has_typed and not candidate_1_1:
        raise ValueError("CORE-016 not_supported: typed endpoints/junctions require MMP 1.1 candidate")
    if has_typed and {"id": "mmp-typed-endpoints", "version": "1.0.0"} not in model.get("extensions", {}).get("mmp_required_capabilities", []):
        raise ValueError("CORE-016 requires explicit mmp-typed-endpoints@1.0.0 capability")
    has_pairs = any("allowed_type_pairs" in relation for relation in model_doc["relationships"])
    if has_pairs and not candidate_1_1:
        raise ValueError("CORE-015 not_supported: pairwise relationships require MMP 1.1 candidate")
    # MMP 1.0 consumers cannot negotiate critical semantics. Fail before packaging.
    from mmp_capability_policy import require_legacy_safe
    if not candidate_1_1:
        require_legacy_safe(model)
    else:
        from mmp_capability_policy import required_capabilities
        required_capabilities(model)
    if has_pairs:
        required = model.setdefault("extensions", {}).get("mmp_required_capabilities", [])
        if {"id": "mmp-pairwise-relationships", "version": "1.0.0"} not in required:
            raise ValueError("CORE-015 requires explicit mmp-pairwise-relationships@1.0.0 capability")
    junction_cap = {"id": "mmp-junction-structure", "version": "0.1.0"}
    declared = junction_cap in model.get("extensions", {}).get("mmp_required_capabilities", [])
    profile_file = "documentation/junction-structure.json"
    if declared != (profile_file in contents):
        raise ValueError("CORE-016 junction profile requires matching mandatory capability and profile document")
    if declared:
        if not candidate_1_1:
            raise ValueError("CORE-016 junction profile not_supported in MMP 1.0")
        profile = json.loads(contents[profile_file])
        schema = json.loads(contents["schemas/mmp-junction-structure-profile.schema.json"])
        Draft202012Validator(schema).validate(profile)
        declared_types = {item["id"] for item in model_doc.get("junctions", [])}
        if set(profile["junction_operators"]) != declared_types:
            raise ValueError("CORE-016 junction profile type coverage mismatch")
    presence_cap = {"id": "mmp-required-default-presence", "version": "0.1.0"}
    presence_name = "documentation/required-default-presence.json"
    presence_declared = presence_cap in model.get("extensions", {}).get("mmp_required_capabilities", [])
    if presence_declared != (presence_name in contents):
        raise ValueError("CORE-009 required/default profile capability/document mismatch")
    if presence_declared:
        if not candidate_1_1:
            raise ValueError("CORE-009 not_supported in MMP 1.0")
        Draft202012Validator(json.loads(contents["schemas/mmp-required-default-presence-profile.schema.json"])).validate(json.loads(contents[presence_name]))
    version = safe_load(contents["canonical/version.yaml"])["version"]["current"]
    namespace = model.get("namespace")
    if not isinstance(namespace, str) or not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", namespace):
        raise ValueError("MMP requires an explicitly approved, stable URI namespace in canonical metamodel.yaml")
    if model["version"] != version:
        raise ValueError("metamodel.version differs from version.current")
    if not skip_validation:
        for script, args in [
            ("validate_canonical_schema.py", ["--model-dir", str(model_dir)]),
            ("validate_semantics.py", [str(model_dir)]),
        ]:
            run = subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                                 cwd=ROOT, text=True, capture_output=True)
            if run.returncode:
                raise ValueError(f"{script} failed (exit {run.returncode}): {run.stderr or run.stdout}")
    entries = {name: f"canonical/{name}.yaml" for name in CORE}
    if "canonical/guidance.yaml" in contents:
        entries["guidance"] = "canonical/guidance.yaml"
    files = [
        {"path": path, "role": "schema" if path.startswith("schemas/") else "documentation" if path.startswith("documentation/") else "canonical",
         "media_type": "application/schema+json" if path.startswith("schemas/") else "application/json" if path.startswith("documentation/") else "application/yaml",
         "sha256": hashlib.sha256(data).hexdigest()}
        for path, data in sorted(contents.items())
    ]
    manifest = {
        "package_format": "mmp", "package_format_version": "1.1.0" if candidate_1_1 else "1.0.0",
        "metamodel": {key: model[key] for key in ("id", "name", "version", "namespace")},
        "producer": {"name": "Metamodel Builder", "version": producer_version},
        "generated_at": timestamp(), "entrypoints": entries, "files": files,
    }
    if candidate_1_1:
        manifest["required_capabilities"] = required_capabilities(model)
    if not skip_validation:
        manifest["validation"] = {
            "structural": "passed", "semantic": "passed",
            "validator": "metamodel-builder", "validator_version": producer_version,
        }
    manifest_schema_name = "mmp-manifest-1-1-candidate.schema.json" if candidate_1_1 else "mmp-manifest-v1.schema.json"
    schema = json.loads((SCHEMAS / manifest_schema_name).read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(manifest)
    payload = yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True).encode("utf-8")
    contents["manifest.yaml"] = payload
    output = output.resolve()
    if as_directory:
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite existing MMP directory: {output}")
        output.mkdir(parents=True)
        for path, data in sorted(contents.items()):
            target = output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    else:
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite existing MMP ZIP: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path, data in sorted(contents.items()):
                info = zipfile.ZipInfo(path, ZIP_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, data)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--producer-version", default="dev")
    parser.add_argument("--directory", action="store_true")
    parser.add_argument("--candidate-1-1", action="store_true", help="Deprecated compatibility alias: MMP 1.1 is now the default")
    parser.add_argument("--legacy-1-0", action="store_true", help="Explicitly export older MMP 1.0 for legacy consumers")
    args = parser.parse_args()
    print(export(args.model_dir, args.output, args.producer_version, as_directory=args.directory, candidate_1_1=not args.legacy_1_0))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"MMP export failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
