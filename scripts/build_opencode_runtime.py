#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, tempfile, zipfile
from pathlib import Path
import yaml
FIXED=(2020,1,1,0,0,0)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def copytree(src,dst):
    if src.exists(): shutil.copytree(src,dst,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','.DS_Store'))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--output',required=True); ap.add_argument('--version',default='0.1.0-dev.14'); a=ap.parse_args()
    root=Path(a.project_root).resolve(); cfg=yaml.safe_load((root/'gpt-project.yaml').read_text(encoding='utf-8'))
    with tempfile.TemporaryDirectory(prefix='metamodel-opencode-') as td:
        out=Path(td)
        for d in ['assistant','schemas','scripts','templates','docs','examples/architecture-lite','workspace']:
            copytree(root/d,out/d)
        shutil.rmtree(out/'examples/architecture-lite/generated',ignore_errors=True)
        core=(out/'assistant/instructions.md').read_text(encoding='utf-8')
        pol=(out/'assistant/policies/opencode-runtime.md').read_text(encoding='utf-8')
        body='# Metamodel Builder – OpenCode\n\n'+core+'\n\n'+pol
        for m in cfg['instructions']['core_contract']['required_markers']:
            if m not in body: raise SystemExit('Missing core marker: '+m)
        (out/'AGENTS.md').write_text(body,encoding='utf-8')
        (out/'.opencode/agents').mkdir(parents=True,exist_ok=True)
        (out/'.opencode/agents/metamodel-builder.md').write_text('''---
description: Skapar, underhåller, validerar och exporterar verktygsneutrala metamodeller med Sparx EA MDG som första målplattform.
mode: primary
---

Arbeta enligt projektets `AGENTS.md`. Läs strukturerad workspace-state före stateful ändringar. Använd inbäddade Python-validatorer och generatorer när deterministisk kontroll finns. Uppdatera canonical YAML eller adapterkällor, aldrig genererad MDG XML som sanningskälla.
''',encoding='utf-8')
        for name,desc,body2 in [
          ('metamodel-validation','Validera canonical YAML, semantik, Sparx-mappning och workspace före progression','1. Läs workspace-state.\n2. Kör schema- och semantikvalidator.\n3. Kör Sparx mapping/MDG-validator när relevant.\n4. Uppdatera state först efter PASS.'),
          ('sparx-mdg','Generera, validera eller reverse-engineera Sparx Enterprise Architect MDG','Canonical YAML är sanningskällan. Validera canonical och mapping före generering. Använd `generate_sparx_mdg.py`, `validate_generated_mdg.py` och `import_sparx_mdg.py` efter behov.')]:
            d=out/f'.opencode/skills/{name}'; d.mkdir(parents=True,exist_ok=True)
            (d/'SKILL.md').write_text(f'---\nname: {name}\ndescription: {desc}\n---\n\n{body2}\n',encoding='utf-8')
        (out/'opencode.jsonc').write_text('{\n  "$schema": "https://opencode.ai/config.json",\n  "default_agent": "metamodel-builder"\n}\n',encoding='utf-8')
        contract={'schema_version':1,'runtime_id':'opencode','capabilities':cfg['capabilities'],'artifacts':cfg['artifacts'],'workspace_state':cfg['workspace_state'],'tools':cfg['tools'],'adapter':{'project_instruction':'AGENTS.md','default_agent':'metamodel-builder','python_scripts':'embedded','shell':'local','git':'workspace_optional'}}
        (out/'runtime-contract.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (out/'VERSION').write_text(a.version+'\n',encoding='utf-8')
        (out/'README.md').write_text(f'''# Metamodel Builder – OpenCode

Version: {a.version}

1. Packa upp ZIP-filen lokalt.
2. Öppna katalogen som workspace i OpenCode.
3. `AGENTS.md` laddas som projektinstruktion och `metamodel-builder` är default-agent.
4. Arbeta i `workspace/` och kör relevanta validators/generatorer före progression.

Python 3 och scriptens Python-beroenden måste finnas lokalt. Ingen modellleverantör är hårdkodad; OpenCodes befintliga provider/model-konfiguration används.
''',encoding='utf-8')
        files=[]
        for f in sorted(out.rglob('*')):
            if f.is_file() and f.name!='MANIFEST.json': files.append({'path':f.relative_to(out).as_posix(),'sha256':sha(f),'size':f.stat().st_size})
        (out/'MANIFEST.json').write_text(json.dumps({'runtime_id':'metamodel-builder-opencode','adapter_id':'opencode','version':a.version,'entrypoint':'AGENTS.md','contract_snapshot':'runtime-contract.json','files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        target=Path(a.output); target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob('*')):
                if f.is_file():
                    info=zipfile.ZipInfo(f.relative_to(out).as_posix(),FIXED); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,f.read_bytes())
    print(target)
if __name__=='__main__': main()
