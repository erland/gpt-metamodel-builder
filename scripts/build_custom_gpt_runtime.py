#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, hashlib, json, shutil, tempfile, zipfile
from pathlib import Path
import yaml
FIXED=(2020,1,1,0,0,0)

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src:Path,dst:Path): dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)

def expand_sources(root:Path, patterns:list[str])->list[Path]:
    found=[]
    for pattern in patterns:
        # pathlib glob handles both literal and wildcard patterns
        matches=list(root.glob(pattern))
        if not matches and (root/pattern).is_file(): matches=[root/pattern]
        for p in matches:
            if p.is_file() and p not in found: found.append(p)
    return found

def compile_instruction(root:Path,cfg:dict)->str:
    base=(root/cfg['instructions']['canonical']).read_text(encoding='utf-8')
    workflow=(root/'assistant/policies/custom-gpt-runtime.md').read_text(encoding='utf-8')
    # Replace the unavailable cross-file workflow pointer with an inline-runtime statement.
    base=base.replace('Följ den explicita workflow-policyn i `assistant/policies/workflow.md`.',
                      'Följ det kompilerade Custom GPT-workflowet nedan.')
    compiled=base.rstrip()+'\n\n'+workflow+'\n'
    markers=cfg['instructions']['core_contract']['required_markers']
    missing=[m for m in markers if m not in compiled]
    if missing: raise SystemExit('Core markers missing after compilation: '+repr(missing))
    limit=int(cfg['runtime']['custom_gpt']['instruction']['max_characters'])
    if len(compiled)>limit: raise SystemExit(f'Compiled instruction too long: {len(compiled)} > {limit}')
    return compiled

def runtime_contract(cfg:dict)->dict:
    tools=[]
    for t in cfg['tools']['tools']:
        state='reduced' if t.get('type') in {'script','local_command'} else 'not_applicable'
        tools.append({**t,'runtime_state':state})
    return {'schema_version':1,'runtime_id':'chatgpt_custom','capabilities':cfg['capabilities'],
            'artifacts':cfg['artifacts'],'workspace_state':cfg['workspace_state'],
            'tools':{**cfg['tools'],'tools':tools},
            'adapter':{'tool_execution':'not_embedded','builder_package':True,
                       'fallback':'Use Data Analysis/code execution where available; never claim an unexecuted deterministic gate passed.'}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--output',required=True); ap.add_argument('--version',default='0.1.0-dev.13'); a=ap.parse_args()
    root=Path(a.project_root).resolve(); cfg=yaml.safe_load((root/'gpt-project.yaml').read_text(encoding='utf-8')); rcfg=cfg['runtime']['custom_gpt']
    with tempfile.TemporaryDirectory(prefix='metamodel-custom-') as td:
        out=Path(td); b=out/'builder'; kp=b/'knowledge-package'; kp.mkdir(parents=True)
        instr=compile_instruction(root,cfg); (b/'instructions.md').write_text(instr,encoding='utf-8')
        # Keep starters short and directly pasteable in Builder.
        raw=(root/'docs/custom-gpt-conversation-starters.md').read_text(encoding='utf-8')
        lines=[ln for ln in raw.splitlines() if ln.startswith('- ')]
        (b/'conversation-starters.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        cap="""# Rekommenderade Builder-funktioner\n\n- Web Search: på (rekommenderad för aktuell extern dokumentation)\n- Code Interpreter & Data Analysis: på (krävs för fil-/YAML-/XML-validering och generering)\n- Image generation: av\n- Filuppladdning/Knowledge: används enligt paketet\n"""
        (b/'capabilities.md').write_text(cap,encoding='utf-8')
        (b/'runtime-contract.json').write_text(json.dumps(runtime_contract(cfg),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

        sources=expand_sources(root,rcfg['knowledge']['sources'])
        # Rank by priority pattern and stable path, then take max files.
        priority=rcfg['knowledge'].get('priority',[])
        def rank(p):
            rel=p.relative_to(root).as_posix(); r=len(priority)+1
            for i,pat in enumerate(priority):
                if fnmatch.fnmatch(rel,pat): r=i; break
            return (r,rel)
        selected=sorted(sources,key=rank)[:int(rcfg['knowledge']['max_files'])]
        used=set()
        for p in selected:
            # Flatten with stable collision-safe names to make Builder upload simple.
            rel=p.relative_to(root).as_posix(); name=rel.replace('/','__')
            if name in used: raise SystemExit('Knowledge name collision: '+name)
            used.add(name); copy(p,kp/name)
        report={'runtime_id':'chatgpt_custom','instruction':{'mode':'compiled','canonical_characters':len((root/cfg['instructions']['canonical']).read_text()),'compiled_characters':len(instr),'max_characters':int(rcfg['instruction']['max_characters']),'core_markers_verified':len(cfg['instructions']['core_contract']['required_markers'])},'knowledge':{'strategy':rcfg['knowledge']['strategy'],'candidates':len(sources),'selected_files':len(selected),'max_files':int(rcfg['knowledge']['max_files']),'selected':[p.relative_to(root).as_posix() for p in selected]},'tool_execution':'not_embedded'}
        (b/'compilation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (out/'README.md').write_text(f"""# Metamodel Builder – Custom GPT\n\nVersion: {a.version}\n\n1. Skapa/öppna en Custom GPT i ChatGPT Builder.\n2. Klistra in `builder/instructions.md` som Instructions.\n3. Lägg in raderna i `builder/conversation-starters.md` som Conversation starters.\n4. Aktivera funktionerna enligt `builder/capabilities.md`.\n5. Ladda upp alla filer i `builder/knowledge-package/` som Knowledge.\n\n`builder/runtime-contract.json` och `builder/compilation-report.json` är verifieringsartefakter och behöver normalt inte laddas upp som Knowledge.\n""",encoding='utf-8')
        (out/'COMPATIBILITY.md').write_text("""# Compatibility\n\n| Område | Custom GPT | Kommentar |\n|---|---|---|\n| Canonical metamodellering | ✅ | Samma semantik och kärninstruktion |\n| Stateful filbaserat workspace | ✅ | Kräver att workspace/projekt bifogas och returneras som filer |\n| Webbaserad standardanalys | ✅ | Web Search bör vara aktiverad |\n| YAML/XML-filgenerering | ✅ | Data Analysis bör vara aktiverad |\n| Inbäddade lokala validators/generatorer | ⚠️ | Scriptfiler är inte inbäddade verktyg i Custom GPT |\n| Deterministisk lokal scriptparitet | ⚠️ | Kör kontroller via Data Analysis när möjligt; rapportera annars begränsningen |\n\nKritiska beteenderegler finns i `builder/instructions.md`; Knowledge används endast som referensmaterial.\n""",encoding='utf-8')
        (out/'VERSION').write_text(a.version+'\n')
        files=[]
        for f in sorted(out.rglob('*')):
            if f.is_file() and f.name!='MANIFEST.json': files.append({'path':f.relative_to(out).as_posix(),'sha256':sha(f),'size':f.stat().st_size})
        man={'runtime_id':'metamodel-builder-custom-gpt','adapter_id':'chatgpt_custom','version':a.version,'entrypoint':'README.md','contract_snapshot':'builder/runtime-contract.json','files':files}
        (out/'MANIFEST.json').write_text(json.dumps(man,ensure_ascii=False,indent=2)+'\n')
        target=Path(a.output); target.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
            for f in sorted(out.rglob('*')):
                if f.is_file():
                    info=zipfile.ZipInfo(f.relative_to(out).as_posix(),FIXED); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,f.read_bytes())
    print(target)
if __name__=='__main__': main()
