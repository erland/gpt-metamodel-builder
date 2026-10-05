#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, tempfile, zipfile
from pathlib import Path

EXPECTED_SCRIPTS={
    "validate_canonical_schema.py",
    "validate_semantics.py",
    "validate_sparx_mapping.py",
    "generate_sparx_mdg.py",
    "validate_generated_mdg.py",
    "generate_documentation.py",
    "export_documentation.py",
    "import_sparx_mdg.py",
    "diff_metamodel.py",
    "adapt_source_model.py",
    "validate_workspace.py",
}

FORBIDDEN={"validate_runtime_parity.py","build_release.py","run_ci.py","lint_gpt_project.py","project_hygiene.py"}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("zipfile")
    a=ap.parse_args()
    errors=[]
    with tempfile.TemporaryDirectory(prefix="validate-plugin-") as td:
        with zipfile.ZipFile(a.zipfile) as z:
            if z.testzip(): errors.append("ZIP CRC failure")
            z.extractall(td)
        root=Path(td)
        required=[
            "plugin.json","runtime-contract.json","README.md","VERSION","MANIFEST.json",
            "skills/metamodel-builder/SKILL.md",
            "skills/metamodel-builder/references/workflow.md",
            "skills/metamodel-builder/schemas/metamodel.schema.json",
            "skills/metamodel-builder/templates/metamodel/metamodel.yaml",
            "skills/metamodel-builder/workspace/state/workspace-state.yaml",
        ]
        for rel in required:
            if not (root/rel).is_file(): errors.append("missing "+rel)

        if (root/"runtime-contract.json").is_file():
            c=json.loads((root/"runtime-contract.json").read_text(encoding="utf-8"))
            if c.get("runtime_id")!="openai_plugin": errors.append("runtime_id mismatch")
            if c.get("compatibility")!="equivalent_runtime_dependent": errors.append("parity mismatch")
            adapter=c.get("adapter",{})
            if adapter.get("skills_first") is not True or adapter.get("workspace_first") is not True:
                errors.append("skills/workspace-first contract missing")
            if adapter.get("state_authority")!="workspace_file": errors.append("state authority mismatch")
            resources=adapter.get("script_resources",{})
            if set(resources.get("packaged",[]))!=EXPECTED_SCRIPTS: errors.append("runtime script closure mismatch")
            if resources.get("mcp_required_for_resource_use") is not False: errors.append("scripts must not require MCP")
            tool_ids={x.get("id") for x in c.get("tools",{}).get("tools",[])}
            if "validate-runtime-parity" in tool_ids: errors.append("CI parity validator leaked into runtime tools")
            if len(tool_ids)!=11: errors.append(f"expected 11 canonical runtime tools, got {len(tool_ids)}")
            fallback=adapter.get("fallback_policy",{})
            if fallback.get("without_code_execution")!="do_not_claim_deterministic_validation_or_generation":
                errors.append("code execution fallback weakened")
            if fallback.get("without_sparx_ea")!="do_not_claim_manual_import_verified":
                errors.append("Sparx EA fallback weakened")

        skill=root/"skills/metamodel-builder/SKILL.md"
        if skill.is_file():
            text=skill.read_text(encoding="utf-8")
            for marker in [
                "Canonical YAML är sanningskällan.",
                "Genererad MDG XML får aldrig bli canonical source.",
                "Validera före generering.",
                "Läs strukturerad projektstatus före nästa steg.",
                "kräver ingen MCP-wrapper",
                "Påstå aldrig att faktisk EA-import passerat",
            ]:
                if marker not in text: errors.append("SKILL missing marker: "+marker)

        script_root=root/"skills/metamodel-builder/scripts"
        actual={p.name for p in script_root.glob("*.py")} if script_root.exists() else set()
        if actual!=EXPECTED_SCRIPTS: errors.append("packaged runtime scripts differ")
        if actual & FORBIDDEN: errors.append("CI/build scripts leaked into Plugin")

        if (root/"MANIFEST.json").is_file():
            man=json.loads((root/"MANIFEST.json").read_text(encoding="utf-8"))
            for item in man.get("files",[]):
                p=root/item["path"]
                if not p.is_file(): errors.append("manifest missing "+item["path"])
                elif hashlib.sha256(p.read_bytes()).hexdigest()!=item["sha256"]:
                    errors.append("checksum mismatch "+item["path"])

    if errors:
        print("OpenAI Plugin runtime validation FAILED")
        for e in errors: print("- "+e)
        return 1
    print("OpenAI Plugin runtime validation PASS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
