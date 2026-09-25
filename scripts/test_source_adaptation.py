#!/usr/bin/env python3
from pathlib import Path
import json, shutil, subprocess, tempfile, yaml
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'examples/source-adaptation/source-catalog.yaml'
APPROVED=ROOT/'examples/source-adaptation/adaptation-plan.yaml'

def run(*args): return subprocess.run(['python3','scripts/adapt_source_model.py',*map(str,args)],cwd=ROOT,text=True,capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); plan=td/'plan.yaml'; out=td/'out'
        p=run('propose',SRC,'--target-id','test_model','--target-name','Test Model','--out',plan); assert p.returncode==0,p.stdout+p.stderr
        d=yaml.safe_load(plan.read_text()); assert d['status']=='draft' and len(d['element_actions'])==3
        p=run('apply',SRC,plan,'--out',out); assert p.returncode==2 and 'status=approved' in p.stderr
        p=run('apply',SRC,APPROVED,'--out',out); assert p.returncode==0,p.stdout+p.stderr
        mm=yaml.safe_load((out/'metamodel.yaml').read_text()); prov=yaml.safe_load((out/'provenance.yaml').read_text())
        assert {x['id'] for x in mm['elements']}=={'capability','application'}
        assert {x['id'] for x in mm['relationships']}=={'application_supports_capability'}
        assert len(prov['mappings'])==3 and prov['sources'][0]['id']=='sample_architecture_source'
        for script in ['validate_canonical_schema.py','validate_semantics.py']:
            q=subprocess.run(['python3',f'scripts/{script}',str(out)],cwd=ROOT,text=True,capture_output=True); assert q.returncode==0,q.stdout+q.stderr
        print(json.dumps({'status':'pass','draft_gate':True,'elements':2,'relationships':1,'provenance_mappings':3},indent=2))
if __name__=='__main__': main()
