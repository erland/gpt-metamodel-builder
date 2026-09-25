#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def run(cmd, cwd):
    print('+', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root', default='.'); ap.add_argument('--reports-dir')
    a=ap.parse_args(); root=Path(a.project_root).resolve(); py=sys.executable
    reports=Path(a.reports_dir).resolve() if a.reports_dir else root/'reports'/'ci'
    reports.mkdir(parents=True, exist_ok=True)

    commands = [
        [py,'scripts/validate_project.py'],
        [py,'scripts/validate_model_robustness.py','--project-root','.'],
        [py,'scripts/validate_canonical_schema.py'],
        [py,'scripts/test_semantic_validator.py'],
        [py,'scripts/test_sparx_mapping.py'],
        [py,'scripts/test_mdg_generator.py'],
        [py,'scripts/test_mdg_validation.py'],
        [py,'scripts/test_documentation_generator.py'],
        [py,'scripts/test_documentation_exports.py'],
        [py,'scripts/test_sparx_importer.py'],
        [py,'scripts/test_metamodel_diff.py'],
        [py,'scripts/test_source_adaptation.py'],
        [py,'scripts/test_workspace_resume.py'],
        [py,'scripts/project_hygiene.py','--project-root','.','--mode','checkpoint','--fix'],
        [py,'scripts/lint_gpt_project.py','--project-root','.'],
        [py,'scripts/project_hygiene.py','--project-root','.','--mode','final'],
    ]
    for cmd in commands: run(cmd, root)
    report={
        'status':'pass',
        'gates':[cmd[1] for cmd in commands],
        'gate_count':len(commands),
    }
    (reports/'ci-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'CI PASS: {len(commands)} gates')
    return 0

if __name__=='__main__': raise SystemExit(main())
