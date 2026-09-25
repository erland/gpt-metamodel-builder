#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, tempfile, zipfile
from pathlib import Path
import yaml

CORE_KEYS = ["capabilities","artifacts","workspace_state"]

def read_json_from_zip(zpath: Path, member: str):
    with zipfile.ZipFile(zpath) as z:
        return json.loads(z.read(member).decode('utf-8'))

def read_text_from_zip(zpath: Path, member: str):
    with zipfile.ZipFile(zpath) as z:
        return z.read(member).decode('utf-8')

def normalize_tools(obj):
    tools=((obj or {}).get('tools') or {}).get('tools',[])
    return {t['id']:{k:v for k,v in t.items() if k!='runtime_state'} for t in tools}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--chat', required=True)
    ap.add_argument('--custom', required=True)
    ap.add_argument('--opencode', required=True)
    ap.add_argument('--json-out')
    a=ap.parse_args()
    root=Path(a.project_root).resolve(); cfg=yaml.safe_load((root/'gpt-project.yaml').read_text(encoding='utf-8'))
    paths={'chatgpt_chat':Path(a.chat),'chatgpt_custom':Path(a.custom),'opencode':Path(a.opencode)}
    contracts={
      'chatgpt_chat':read_json_from_zip(paths['chatgpt_chat'],'assistant/runtime-contract.json'),
      'chatgpt_custom':read_json_from_zip(paths['chatgpt_custom'],'builder/runtime-contract.json'),
      'opencode':read_json_from_zip(paths['opencode'],'runtime-contract.json')
    }
    errors=[]; warnings=[]
    markers=cfg['instructions']['core_contract']['required_markers']
    instructions={
      'chatgpt_chat':read_text_from_zip(paths['chatgpt_chat'],'assistant/instructions.md'),
      'chatgpt_custom':read_text_from_zip(paths['chatgpt_custom'],'builder/instructions.md'),
      'opencode':read_text_from_zip(paths['opencode'],'AGENTS.md')
    }
    for rid,txt in instructions.items():
        for m in markers:
            if m not in txt: errors.append(f'{rid}: missing core marker: {m}')
    for key in CORE_KEYS:
        baseline=contracts['chatgpt_chat'].get(key)
        for rid in ['chatgpt_custom','opencode']:
            if contracts[rid].get(key)!=baseline: errors.append(f'{rid}: {key} contract drift')
    base_tools=normalize_tools(contracts['chatgpt_chat'])
    for rid in ['chatgpt_custom','opencode']:
        if normalize_tools(contracts[rid])!=base_tools: errors.append(f'{rid}: tool contract drift')
    # Explicitly allowed execution differences.
    custom_states={t['id']:t.get('runtime_state') for t in contracts['chatgpt_custom']['tools']['tools']}
    if any(v!='reduced' for v in custom_states.values()): warnings.append('Custom GPT contains non-reduced local tool state; review manually.')
    oc_adapter=contracts['opencode'].get('adapter',{})
    if oc_adapter.get('python_scripts')!='embedded': errors.append('opencode: embedded python scripts expected')
    report={
      'status':'pass' if not errors else 'fail',
      'runtimes':list(paths),
      'core_markers':len(markers),
      'contract_sections_verified':CORE_KEYS+['tools'],
      'allowed_differences':{
        'chatgpt_chat':'Embedded scripts and file-based workspace in Chat runtime.',
        'chatgpt_custom':'Local scripts are not executable runtime tools; Data Analysis/code execution is fallback and deterministic gates must not be claimed unless executed.',
        'opencode':'Embedded Python scripts, local shell and optional Git workspace integration.'
      },
      'errors':errors,'warnings':warnings
    }
    if a.json_out: Path(a.json_out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if errors:
        print('Runtime parity FAILED'); [print('- '+e) for e in errors]; return 1
    print('Runtime parity PASS')
    print(f'Core markers: {len(markers)}; contract sections: {len(report["contract_sections_verified"])}')
    return 0
if __name__=='__main__': raise SystemExit(main())
