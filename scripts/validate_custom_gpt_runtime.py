#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile, zipfile
from pathlib import Path
import yaml

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--zip',required=True); a=ap.parse_args()
    root=Path(a.project_root).resolve(); cfg=yaml.safe_load((root/'gpt-project.yaml').read_text()); zpath=Path(a.zip)
    errors=[]
    with tempfile.TemporaryDirectory(prefix='validate-custom-') as td:
        with zipfile.ZipFile(zpath) as z: z.extractall(td)
        d=Path(td)
        required=['builder/instructions.md','builder/conversation-starters.md','builder/capabilities.md','builder/runtime-contract.json','builder/compilation-report.json','README.md','COMPATIBILITY.md','VERSION','MANIFEST.json']
        for rel in required:
            if not (d/rel).is_file(): errors.append('Missing '+rel)
        instr=(d/'builder/instructions.md').read_text(encoding='utf-8') if (d/'builder/instructions.md').exists() else ''
        lim=int(cfg['runtime']['custom_gpt']['instruction']['max_characters'])
        if len(instr)>lim: errors.append(f'Instruction too long {len(instr)} > {lim}')
        for marker in cfg['instructions']['core_contract']['required_markers']:
            if marker not in instr: errors.append('Missing core marker: '+marker)
        kp=d/'builder/knowledge-package'; kfiles=[p for p in kp.rglob('*') if p.is_file()] if kp.exists() else []
        if len(kfiles)>int(cfg['runtime']['custom_gpt']['knowledge']['max_files']): errors.append('Too many knowledge files')
        man=json.loads((d/'MANIFEST.json').read_text()) if (d/'MANIFEST.json').exists() else {'files':[]}
        for item in man.get('files',[]):
            p=d/item['path']
            if not p.exists(): errors.append('Manifest missing file '+item['path']); continue
            if hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']: errors.append('Checksum mismatch '+item['path'])
        contract=json.loads((d/'builder/runtime-contract.json').read_text()) if (d/'builder/runtime-contract.json').exists() else {}
        if contract.get('runtime_id')!='chatgpt_custom': errors.append('Wrong runtime_id')
        if any('/scripts/' in '/'+x['path'] or x['path'].startswith('scripts/') for x in man.get('files',[])): errors.append('Scripts must not be embedded as executable runtime tools')
    if errors:
        for e in errors: print('ERROR:',e)
        raise SystemExit(1)
    print(f'Custom GPT runtime OK: instruction={len(instr)} chars, knowledge={len(kfiles)} files')
if __name__=='__main__': main()
