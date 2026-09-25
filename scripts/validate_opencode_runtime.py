#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile, zipfile
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('zipfile'); a=ap.parse_args(); errors=[]
    with tempfile.TemporaryDirectory(prefix='validate-opencode-') as td:
        with zipfile.ZipFile(a.zipfile) as z: z.extractall(td)
        root=Path(td)
        req=['AGENTS.md','opencode.jsonc','.opencode/agents/metamodel-builder.md','.opencode/skills/metamodel-validation/SKILL.md','.opencode/skills/sparx-mdg/SKILL.md','runtime-contract.json','scripts/validate_canonical_schema.py','scripts/validate_semantics.py','scripts/generate_sparx_mdg.py','workspace/state/workspace-state.yaml','MANIFEST.json','VERSION']
        for x in req:
            if not (root/x).is_file(): errors.append('missing '+x)
        if (root/'AGENTS.md').is_file():
            t=(root/'AGENTS.md').read_text(encoding='utf-8')
            for m in ['Canonical YAML är sanningskällan.','Genererad MDG XML får aldrig bli canonical source.','Validera före generering.','Läs strukturerad projektstatus före nästa steg.']:
                if m not in t: errors.append('missing core marker '+m)
        if (root/'opencode.jsonc').is_file() and '"default_agent": "metamodel-builder"' not in (root/'opencode.jsonc').read_text(encoding='utf-8'): errors.append('default agent not configured')
        if (root/'MANIFEST.json').is_file():
            man=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
            for i in man.get('files',[]):
                p=root/i['path']
                if not p.is_file(): errors.append('manifest missing '+i['path'])
                elif hashlib.sha256(p.read_bytes()).hexdigest()!=i['sha256']: errors.append('checksum mismatch '+i['path'])
    if errors:
        print('OpenCode runtime validation FAILED'); [print('- '+e) for e in errors]; return 1
    print('OpenCode runtime validation PASS'); print('AGENTS/default agent/skills: OK'); print('Embedded scripts: OK'); print('Manifest checksums: OK'); return 0
if __name__=='__main__': raise SystemExit(main())
