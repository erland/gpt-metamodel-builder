#!/usr/bin/env python3
from pathlib import Path
import shutil, tempfile, subprocess, sys, yaml
ROOT=Path(__file__).resolve().parents[1]
def main():
    with tempfile.TemporaryDirectory() as td:
        dst=Path(td)/'workspace-copy'; shutil.copytree(ROOT/'workspace',dst)
        state=yaml.safe_load((dst/'state/workspace-state.yaml').read_text(encoding='utf-8'))
        assert state['resume']['portable'] is True
        assert state['resume']['conversation_required'] is False
        for p in state['resume']['required_paths']: assert (dst/p).exists(), p
    print('Workspace portable resume test OK')
if __name__=='__main__': main()
