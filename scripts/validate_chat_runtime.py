#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path

REQUIRED = {
    'START-HERE.md', 'VERSION', 'MANIFEST.json',
    'assistant/instructions.md', 'assistant/runtime-contract.json',
}

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--zip', required=True)
    a=ap.parse_args(); zpath=Path(a.zip)
    errors=[]
    try:
        with zipfile.ZipFile(zpath) as z:
            names=set(z.namelist())
            for name in sorted(REQUIRED):
                if name not in names: errors.append(f'missing {name}')
            if 'MANIFEST.json' in names:
                manifest=json.loads(z.read('MANIFEST.json'))
                if manifest.get('adapter_id')!='chatgpt_chat': errors.append('manifest adapter_id must be chatgpt_chat')
                for item in manifest.get('files',[]):
                    p=item.get('path')
                    if p not in names:
                        errors.append(f'manifest references missing file: {p}')
                        continue
                    if sha(z.read(p)) != item.get('sha256'):
                        errors.append(f'checksum mismatch: {p}')
            if 'assistant/runtime-contract.json' in names:
                contract=json.loads(z.read('assistant/runtime-contract.json'))
                if contract.get('runtime_id')!='chatgpt_chat': errors.append('runtime_id must be chatgpt_chat')
    except Exception as exc:
        errors.append(str(exc))
    if errors:
        print('Chat runtime validation FAILED')
        for e in errors: print('- '+e)
        return 1
    print('Chat runtime validation PASS')
    return 0

if __name__=='__main__': raise SystemExit(main())
