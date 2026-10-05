#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, shutil, tempfile, zipfile
from pathlib import Path
import yaml

FIXED=(2020,1,1,0,0,0)
RUNTIME_SCRIPTS=[
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
]

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def copytree(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.pyo",".DS_Store"))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",default=".")
    ap.add_argument("--output",required=True)
    ap.add_argument("--version",required=True)
    a=ap.parse_args()
    root=Path(a.project_root).resolve()
    cfg=yaml.safe_load((root/"gpt-project.yaml").read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="metamodel-plugin-") as td:
        out=Path(td)
        skill=out/"skills"/"metamodel-builder"
        (skill/"scripts").mkdir(parents=True)
        for d in ["schemas","templates","metamodel","platforms","workspace","docs","examples"]:
            copytree(root/d,skill/d)
        shutil.rmtree(skill/"examples"/"architecture-lite"/"generated",ignore_errors=True)

        for name in RUNTIME_SCRIPTS:
            shutil.copy2(root/"scripts"/name,skill/"scripts"/name)

        workflow=skill/"references"
        workflow.mkdir(parents=True)
        shutil.copy2(root/"assistant"/"policies"/"workflow.md",workflow/"workflow.md")

        canonical=(root/"assistant"/"instructions.md").read_text(encoding="utf-8").strip()
        skill_text=(
            "---\n"
            "name: metamodel-builder\n"
            "description: Skapa, underhåll, validera och exportera verktygsneutrala metamodeller med deterministiska generatorer och Sparx EA MDG som första målplattform.\n"
            "---\n\n"
            "# Metamodel Builder\n\n"
            "## Plugin-runtime\n\n"
            "- Canonical YAML är alltid sanningskälla; genererad MDG XML får aldrig bli canonical source.\n"
            "- Läs strukturerad workspace-state före progression; chatthistorik ersätter aldrig projektstatus.\n"
            "- Full parity kräver persistent writable workspace och kompatibel Python/code execution.\n"
            "- Kör schema- och semantikvalidering före generering och korrigera fel innan progression.\n"
            "- Paketerade Pythonfiler är canonical runtime-tools/resources och kräver ingen MCP-wrapper enbart för att användas.\n"
            "- Om ett verktyg inte faktiskt kan köras får motsvarande deterministiska gate inte påstås ha passerat.\n"
            "- PDF-export är dependency-/hostberoende; påstå aldrig att en PDF skapats om artefakten saknas.\n"
            "- Sparx EA-importfixture är extern praktisk verifiering. Påstå aldrig att faktisk EA-import passerat om ingen EA-miljö användes.\n"
            "- Följ workflow-policyn i references/workflow.md.\n\n"
            "## Canonical behavior\n\n"
            + canonical + "\n"
        )
        (skill/"SKILL.md").write_text(skill_text,encoding="utf-8")

        plugin={
            "$schema":"https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name":"metamodel-builder",
            "version":a.version,
            "description":cfg["project"]["description"].strip(),
        }
        (out/"plugin.json").write_text(json.dumps(plugin,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

        contract={
            "schema_version":1,
            "runtime_id":"openai_plugin",
            "version":a.version,
            "compatibility":"equivalent_runtime_dependent",
            "capabilities":cfg["capabilities"],
            "artifacts":cfg["artifacts"],
            "workspace_state":cfg["workspace_state"],
            "tools":cfg["tools"],
            "adapter":{
                "mode":"openai_plugin",
                "skills_first":True,
                "workspace_first":True,
                "entrypoint":"skills/metamodel-builder/SKILL.md",
                "state_authority":"workspace_file",
                "state_path":"project-status.yaml",
                "mcp_generated":False,
                "script_resources":{
                    "packaged":RUNTIME_SCRIPTS,
                    "mcp_required_for_resource_use":False,
                    "execution":"host_code_execution_when_available",
                },
                "host_requirements":{
                    "filesystem_read":"required",
                    "filesystem_write":"required",
                    "persistent_state":"required",
                    "code_execution":"required_for_full_parity",
                    "shell":"recommended",
                    "reportlab":"required_only_for_pdf_export",
                    "sparx_ea":"external_manual_verification_only",
                },
                "fallback_policy":{
                    "without_code_execution":"do_not_claim_deterministic_validation_or_generation",
                    "without_pdf_dependency":"deliver_available_formats_only",
                    "without_sparx_ea":"do_not_claim_manual_import_verified",
                },
            },
        }
        (out/"runtime-contract.json").write_text(json.dumps(contract,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        (out/"README.md").write_text(
            f"# Metamodel Builder – OpenAI Plugin\n\nVersion: {a.version}\n\n"
            "Skills-first equivalent_runtime_dependent peer runtime. Full modell-/generatorparitet kräver persistent writable workspace och kompatibel Python-exekvering. Paketerade scripts kräver ingen MCP-wrapper.\n",
            encoding="utf-8"
        )
        (out/"VERSION").write_text(a.version+"\n",encoding="utf-8")

        files=[]
        for f in sorted(out.rglob("*")):
            if f.is_file() and f.name!="MANIFEST.json":
                files.append({"path":f.relative_to(out).as_posix(),"sha256":sha(f),"size":f.stat().st_size})
        (out/"MANIFEST.json").write_text(json.dumps({
            "runtime_id":"metamodel-builder-plugin",
            "adapter_id":"openai_plugin",
            "version":a.version,
            "entrypoint":"skills/metamodel-builder/SKILL.md",
            "contract_snapshot":"runtime-contract.json",
            "files":files,
        },ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

        target=Path(a.output)
        target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,"w",zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    rel=f.relative_to(out).as_posix()
                    info=zipfile.ZipInfo(rel,FIXED)
                    info.compress_type=zipfile.ZIP_DEFLATED
                    info.external_attr=(0o755 if rel.startswith("skills/metamodel-builder/scripts/") and f.suffix==".py" else 0o644)<<16
                    z.writestr(info,f.read_bytes())
    print(target)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
