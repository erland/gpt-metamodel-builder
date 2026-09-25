#!/usr/bin/env python3
from pathlib import Path
import json, sys, yaml
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
WS=ROOT/'workspace'
def main():
    state=yaml.safe_load((WS/'state/workspace-state.yaml').read_text(encoding='utf-8'))
    schema=json.loads((ROOT/'schemas/workspace-runtime-state.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(state)
    missing=[p for p in state['resume']['required_paths'] if not (WS/p).exists()]
    if missing: raise ValueError('Missing resume paths: '+', '.join(missing))
    log=yaml.safe_load((WS/'state/change-log.yaml').read_text(encoding='utf-8'))
    if not isinstance(log,dict) or not isinstance(log.get('changes'),list): raise ValueError('Invalid change log')
    if state['resume']['conversation_required'] is not False: raise ValueError('Conversation must not be required')
    print('Workspace resume contract OK')
if __name__=='__main__':
    try: main()
    except Exception as e: print(e,file=sys.stderr); sys.exit(1)
