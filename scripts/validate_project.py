#!/usr/bin/env python3
from pathlib import Path
import json, sys, yaml
from jsonschema import Draft202012Validator
ROOT = Path(__file__).resolve().parents[1]
def load_yaml(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
    return data
def main():
    cfg = load_yaml(ROOT / "gpt-project.yaml")
    status = load_yaml(ROOT / "project-status.yaml")
    schema = json.loads((ROOT / "schemas/project-status.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(status)
    required = ["assistant/instructions.md","assistant/policies/workflow.md","docs/development-plan.md","schemas/metamodel.schema.json","schemas/properties.schema.json","schemas/constraints.schema.json","schemas/viewpoints.schema.json","schemas/notation.schema.json","schemas/provenance.schema.json","schemas/version.schema.json","schemas/guidance.schema.json","docs/canonical-metamodel-v1.md","docs/modeling-guidance-v1.md","scripts/export_documentation.py","docs/source-adaptation-v1.md","schemas/source-catalog.schema.json","schemas/adaptation-plan.schema.json","scripts/adapt_source_model.py","PROJECT.md","STATUS.md"]
    missing = [p for p in required if not (ROOT / p).is_file()]
    if missing: raise ValueError("Missing required files: " + ", ".join(missing))
    required_runtime_ids={"chatgpt_chat","chatgpt_custom","claude_project","opencode","openai_plugin"}
    actual={x["runtime_id"] for x in cfg["analysis"]["runtime"]["candidates"]}
    if actual != required_runtime_ids: raise ValueError(f"Runtime candidate set mismatch: {sorted(actual)}")
    print("Project foundation contract OK")
    return 0
if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
