#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, cwd):
    print('+', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--version', required=True)
    a=ap.parse_args(); root=Path(a.project_root).resolve(); out=Path(a.output_dir).resolve(); py=sys.executable
    pid='metamodel-builder'
    project=out/f'{pid}-project-{a.version}.zip'
    chat=out/f'{pid}-chat-{a.version}.zip'
    custom=out/f'{pid}-custom-gpt-{a.version}.zip'
    opencode=out/f'{pid}-opencode-{a.version}.zip'
    for p in [project,chat,custom,opencode,out/'release-manifest.json',out/'runtime-parity.json',out/'SHA256SUMS.txt']:
        if not p.is_file(): raise SystemExit(f'Missing release artifact: {p}')
    run([py,'scripts/validate_chat_runtime.py','--zip',chat], root)
    run([py,'scripts/validate_custom_gpt_runtime.py','--project-root','.','--zip',custom], root)
    run([py,'scripts/validate_opencode_runtime.py',opencode], root)
    parity_check=out/'runtime-parity-validation.json'
    run([py,'scripts/validate_runtime_parity.py','--project-root','.','--chat',chat,'--custom',custom,'--opencode',opencode,'--json-out',parity_check], root)
    manifest=json.loads((out/'release-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('version') != a.version: raise SystemExit('Release manifest version mismatch')
    declared={x['name']:x for x in manifest.get('artifacts',[])}
    for p in [project,chat,custom,opencode,out/'runtime-parity.json']:
        item=declared.get(p.name)
        if not item: raise SystemExit(f'Manifest missing artifact: {p.name}')
        if item.get('sha256') != sha(p): raise SystemExit(f'Manifest checksum mismatch: {p.name}')
    sums={}
    for line in (out/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        h,name=line.split('  ',1); sums[name]=h
    for name,h in sums.items():
        p=out/name
        if not p.is_file(): raise SystemExit(f'SHA256SUMS references missing file: {name}')
        if sha(p)!=h: raise SystemExit(f'SHA256SUMS mismatch: {name}')
    print('Distribution validation PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
