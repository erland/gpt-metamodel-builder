#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, tempfile, zipfile
from pathlib import Path
import yaml
FIXED=(2020,1,1,0,0,0)

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def copytree(src:Path,dst:Path):
    if src.exists(): shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--output',required=True); ap.add_argument('--version',default='0.1.0-dev.12'); a=ap.parse_args()
    root=Path(a.project_root).resolve(); cfg=yaml.safe_load((root/'gpt-project.yaml').read_text())
    with tempfile.TemporaryDirectory(prefix='metamodel-chat-') as td:
        out=Path(td)
        (out/'assistant/policies').mkdir(parents=True); (out/'schemas').mkdir(); (out/'scripts').mkdir(); (out/'templates').mkdir(); (out/'knowledge').mkdir()
        shutil.copy2(root/'assistant/instructions.md',out/'assistant/instructions.md')
        for f in (root/'assistant/policies').glob('*.md'): shutil.copy2(f,out/'assistant/policies'/f.name)
        for f in (root/'schemas').glob('*.json'): shutil.copy2(f,out/'schemas'/f.name)
        copytree(root/'templates',out/'templates')
        for tool in cfg['tools']['tools']:
            if tool.get('type')=='script':
                s=root/tool['script']; shutil.copy2(s,out/'scripts'/s.name)
        copytree(root/'scripts/lib',out/'scripts/lib')
        for f in (root/'docs').glob('*.md'): shutil.copy2(f,out/'knowledge'/f.name)
        copytree(root/'examples/architecture-lite',out/'knowledge/examples/architecture-lite')
        shutil.rmtree(out/'knowledge/examples/architecture-lite/generated',ignore_errors=True)
        contract={'schema_version':1,'runtime_id':'chatgpt_chat',**{k:cfg[k] for k in ['capabilities','artifacts','workspace_state','tools']}}
        (out/'assistant/runtime-contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n')
        (out/'VERSION').write_text(a.version+'\n')
        (out/'START-HERE.md').write_text(f'''# Metamodel Builder – Chat ZIP\n\nDen här ZIP-filen är den portabla Chat-runtime-distributionen för **Metamodel Builder**.\n\nBifoga ZIP-filen i en ChatGPT-konversation och ange att den ska användas som GPT i konversationen. För ett befintligt metamodellprojekt bifogar du även projektets/workspacets ZIP.\n\nViktiga delar: `assistant/`, `schemas/`, `scripts/`, `templates/` och `knowledge/`.\n\nVersion: {a.version}\n''')
        files=[]
        for f in sorted(out.rglob('*')):
            if f.is_file() and f.name!='MANIFEST.json': files.append({'path':f.relative_to(out).as_posix(),'sha256':sha(f),'size':f.stat().st_size})
        man={'runtime_id':'metamodel-builder-chat','adapter_id':'chatgpt_chat','version':a.version,'entrypoint':'START-HERE.md','contract_snapshot':'assistant/runtime-contract.json','files':files}
        (out/'MANIFEST.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n')
        target=Path(a.output); target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob('*')):
                if f.is_file():
                    info=zipfile.ZipInfo(f.relative_to(out).as_posix(),FIXED); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,f.read_bytes())
    print(target)
if __name__=='__main__': main()
