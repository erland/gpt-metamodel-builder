#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

FIXED=(2020,1,1,0,0,0)
EXCLUDE_DIRS={'.git','build','dist','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache'}

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, cwd):
    print('+', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)

def zip_project(root: Path, target: Path):
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(root.rglob('*')):
            if not f.is_file(): continue
            rel=f.relative_to(root)
            if any(part in EXCLUDE_DIRS for part in rel.parts): continue
            if f.suffix in {'.pyc','.pyo'}: continue
            info=zipfile.ZipInfo((Path(root.name)/rel).as_posix(), FIXED)
            info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
            z.writestr(info, f.read_bytes())

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--skip-ci', action='store_true')
    a=ap.parse_args(); root=Path(a.project_root).resolve(); out=Path(a.output_dir).resolve(); out.mkdir(parents=True,exist_ok=True); py=sys.executable
    if not a.skip_ci: run([py,'scripts/run_ci.py','--project-root','.','--reports-dir',str(out/'ci-reports')], root)
    pid='metamodel-builder'
    chat=out/f'{pid}-chat-{a.version}.zip'
    custom=out/f'{pid}-custom-gpt-{a.version}.zip'
    opencode=out/f'{pid}-opencode-{a.version}.zip'
    project=out/f'{pid}-project-{a.version}.zip'
    run([py,'scripts/build_chat_runtime.py','--project-root','.','--output',chat,'--version',a.version], root)
    run([py,'scripts/build_custom_gpt_runtime.py','--project-root','.','--output',custom,'--version',a.version], root)
    run([py,'scripts/build_opencode_runtime.py','--project-root','.','--output',opencode,'--version',a.version], root)
    run([py,'scripts/validate_chat_runtime.py','--zip',chat], root)
    run([py,'scripts/validate_custom_gpt_runtime.py','--project-root','.','--zip',custom], root)
    run([py,'scripts/validate_opencode_runtime.py',opencode], root)
    parity=out/'runtime-parity.json'
    run([py,'scripts/validate_runtime_parity.py','--project-root','.','--chat',chat,'--custom',custom,'--opencode',opencode,'--json-out',parity], root)
    zip_project(root, project)
    artifacts=[project,chat,custom,opencode,parity]
    manifest={'project_id':pid,'version':a.version,'artifacts':[]}
    for p in artifacts:
        manifest['artifacts'].append({'name':p.name,'sha256':digest(p),'size':p.stat().st_size})
    manifest_path=out/'release-manifest.json'; manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sums=out/'SHA256SUMS.txt'; sums.write_text(''.join(f'{digest(p)}  {p.name}\n' for p in [project,chat,custom,opencode,parity,manifest_path]),encoding='utf-8')
    print(f'Release build PASS: {a.version}')
    return 0

if __name__=='__main__': raise SystemExit(main())
