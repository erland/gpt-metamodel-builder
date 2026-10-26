#!/usr/bin/env python3
"""Generate a reviewable, non-mutating MMP 1.1 semantic-upgrade plan.

Proposals are suggestions for *review*, not inferred relationship permissions.
Only explicit user-approved decisions can be applied by a separate future step.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml

from import_mmp import execute as import_execute, read_package, load_manifest


def plan(source: Path) -> dict:
    # Use real package validation; do not inspect potentially malicious YAML alone.
    verified = import_execute(source, "validate")
    files = read_package(source)
    manifest = load_manifest(files)
    model = yaml.safe_load(files[manifest["entrypoints"]["metamodel"]])
    elements = {item["id"] for item in model.get("elements", [])}
    relations = {item["id"] for item in model.get("relationships", [])}
    junctions = {item["id"] for item in model.get("junctions", [])}
    proposals = []
    for rel in model.get("relationships", []):
        source_types = rel.get("source", {}).get("types", [])
        target_types = rel.get("target", {}).get("types", [])
        options = []
        if source_types and target_types and not rel.get("allowed_type_pairs"):
            options.append({
                "feature": "allowed_type_pairs",
                "reason": "Exact permitted source/target pairs are not defined",
                "known_source_types": source_types,
                "known_target_types": target_types,
                "warning": "These are candidate domains, not automatically approved pairs",
            })
        if not rel.get("allowed_typed_pairs"):
            options.append({
                "feature": "allowed_typed_pairs",
                "reason": "Typed relation/junction endpoints are not explicitly constrained",
                "warning": "No typed pair can be inferred from the source alone",
            })
        if options:
            proposals.append({
                "relationship_id": rel["id"],
                "review_status": "pending_user_decision",
                "choices": ["defer", "keep_existing", "specify_explicit_rules"],
                "selected_choice": None,
                "options": options,
            })
    return {
        "plan_format": "mmp-semantic-upgrade-plan",
        "plan_version": "1.0.0",
        "source_package_format": verified["package_format_version"],
        "target_package_format": "1.1.0",
        "source_metamodel": manifest["metamodel"],  # metadata, not source transformation
        "scope": {"element_types": len(elements), "relationship_types": len(relations),
                  "junction_types": len(junctions)},
        "review_required": True,
        "automatic_semantic_changes": False,
        "default_decision": "defer",
        "recommendations": proposals,
        "global_review": [
            {"feature": "junction-structure", "status": "review",
             "note": "Introduce structure only from supplied authoritative modeling rules"},
            {"feature": "typed-endpoints", "status": "review",
             "note": "Explicitly choose whether relationship and junction endpoints are required"},
        ],
        "instructions": "Review each relationship and choose defer, keep_existing, or specify_explicit_rules. No inferred pairs should be applied without documented evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite existing review plan")
    result = plan(args.package)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Semantic upgrade plan: {args.output} ({len(result['recommendations'])} relationships to review)")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        import sys
        print(f"Semantic upgrade planning failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
