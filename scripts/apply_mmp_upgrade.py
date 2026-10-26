#!/usr/bin/env python3
"""Apply explicitly reviewed MMP 1.1 pair rules without modifying the source.

The review plan is bound to the exact input package by SHA-256. Only the
allowed_type_pairs feature is writable in this first implementation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import yaml
from import_mmp import execute as import_execute
from export_mmp import export
from plan_mmp_upgrade import plan as generate_plan


def apply(source: Path, decisions: Path, output: Path, report: Path) -> dict:
    source, decisions, output, report = [x.resolve() for x in (source, decisions, output, report)]
    if len({source, decisions, output, report}) != 4 or output.exists() or report.exists():
        raise ValueError("Distinct, unused paths required; refusing to overwrite")
    baseline = generate_plan(source)
    if baseline["source_package_format"] != "1.1.0":
        raise ValueError("Format-migrate to MMP 1.1 before semantic upgrade")
    provided = json.loads(decisions.read_text(encoding="utf-8"))
    if not isinstance(provided, dict) or provided.get("plan_format") != baseline["plan_format"]:
        raise ValueError("Invalid semantic upgrade plan")
    if provided.get("source_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
        raise ValueError("Review plan does not match the exact source package")
    original = {r["relationship_id"]: r for r in baseline["recommendations"]}
    selected = provided.get("decisions")
    if not isinstance(selected, list) or len(selected) != len(original):
        raise ValueError("One explicit decision is required per proposed relationship")
    indexed = {}
    for item in selected:
        if not isinstance(item, dict) or item.get("relationship_id") not in original:
            raise ValueError("Unknown relationship in decisions")
        rid = item["relationship_id"]
        if rid in indexed: raise ValueError("Duplicate relationship decision")
        if item.get("choice") not in ("defer", "keep_existing", "specify_explicit_rules"):
            raise ValueError("Missing/invalid review choice")
        if item["choice"] == "specify_explicit_rules":
            pairs = item.get("allowed_type_pairs")
            if not isinstance(pairs, list) or not pairs:
                raise ValueError("Explicit rules require a non-empty pair list")
            if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
                raise ValueError("Explicit rules require supporting evidence")
            if any(not isinstance(x, dict) or set(x) != {"source", "target"}
                   or not all(isinstance(v, str) for v in x.values()) for x in pairs):
                raise ValueError("Invalid allowed_type_pairs structure")
        elif set(item) != {"relationship_id", "choice"}:
            raise ValueError("Non-applying choices must not contain rules")
        indexed[rid] = item

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        model_dir = work / "canonical"
        import_execute(source, "import", model_dir)
        model_path = model_dir / "metamodel.yaml"
        doc = yaml.safe_load(model_path.read_text(encoding="utf-8"))
        changes = []
        for rel in doc["relationships"]:
            decision = indexed.get(rel["id"])
            if not decision or decision["choice"] != "specify_explicit_rules": continue
            if rel.get("allowed_type_pairs"):
                raise ValueError("Cannot replace existing pair rules in initial upgrader")
            pairs = decision["allowed_type_pairs"]
            sources = set(rel["source"]["types"])
            targets = set(rel["target"]["types"])
            for pair in pairs:
                if pair["source"] not in sources or pair["target"] not in targets:
                    raise ValueError(f"Pair outside declared relationship domains: {rel['id']}")
            if len({(x["source"], x["target"]) for x in pairs}) != len(pairs):
                raise ValueError(f"Duplicate explicit pair: {rel['id']}")
            rel["allowed_type_pairs"] = pairs
            changes.append({"relationship_id": rel["id"], "before": None,
                            "after": pairs, "evidence": decision["evidence"]})
        if changes:
            cap = {"id": "mmp-pairwise-relationships", "version": "1.0.0"}
            required = doc["metamodel"].setdefault("extensions", {}).setdefault(
                "mmp_required_capabilities", [])
            if cap not in required: required.append(cap)
            model_path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True),
                                  encoding="utf-8")
        candidate = work / "new.mmp.zip"
        export(model_dir, candidate, "dev", candidate_1_1=True)
        verified = import_execute(candidate, "validate")
        restored = work / "restored"
        import_execute(candidate, "import", restored)
        if yaml.safe_load((restored / "metamodel.yaml").read_text()) != doc:
            raise ValueError("Semantic roundtrip mismatch")
        audit = {"status": "pass", "mode": "approved_semantic_upgrade",
                 "source_sha256": provided["source_sha256"],
                 "changes": changes, "changed_relationships": len(changes),
                 "decisions_reviewed": len(indexed),
                 "other_canonical_files_preserved": True,
                 "validation": "schema, semantics, MMP 1.1 and reimport passed",
                 "summary": verified["summary"]}
        # Preserve all other canonical YAML bytes, not only semantic equivalence.
        for name in ("properties", "constraints", "viewpoints", "notation", "provenance",
                     "version", "guidance"):
            f = model_dir / (name + ".yaml")
            if f.is_file() and (restored / f.name).read_bytes() != f.read_bytes():
                raise ValueError(f"Unexpected canonical file change: {name}")
        output.parent.mkdir(parents=True, exist_ok=True)
        report.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(candidate.read_bytes())
        try:
            report.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
        except Exception:
            output.unlink()
            raise
        return audit


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("package", type=Path)
    ap.add_argument("--decisions", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    a = ap.parse_args()
    print(json.dumps(apply(a.package, a.decisions, a.output, a.report), indent=2))


if __name__ == "__main__":
    try: main()
    except Exception as exc:
        import sys
        print(f"MMP approved upgrade failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
