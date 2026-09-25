#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile, yaml, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate_canonical_schema as canonical_schema

def run(*args):
    p=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p

def main():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'imported'
        run('python3','scripts/import_sparx_mdg.py','--input','generated/architecture-lite-mdg.xml','--output',str(out),'--json')
        errs=canonical_schema.validate_package(out/'canonical')
        if errs: raise RuntimeError('\n'.join(errs))
        run('python3','scripts/validate_semantics.py',str(out/'canonical'))
        run('python3','scripts/validate_sparx_mapping.py','--canonical',str(out/'canonical'),'--adapter',str(out/'platforms/sparx-ea'))
        rep=yaml.safe_load((out/'intermediate/mdg-import.yaml').read_text(encoding='utf-8'))
        c=rep['counts']
        assert c['stereotypes']==7 and c['elements']==4 and c['relationships']==3
        assert c['diagrams']==2 and c['quick_linker_rules']==3 and c['shape_scripts']==4
        for f in ['capability.shape','application.shape','platform.shape','business_process.shape']:
            assert (out/'platforms/sparx-ea/shapescripts'/f).is_file()
        regenerated=Path(td)/'regenerated.xml'
        run('python3','scripts/generate_sparx_mdg.py','--project-root','.', '--canonical',str(out/'canonical'),'--adapter',str(out/'platforms/sparx-ea'),'--output',str(regenerated))
        text=regenerated.read_text(encoding='utf-8')
        for name in ['Capability','Application','Platform','Business Process','Application realizes Capability','Platform supports Application']:
            assert f'name="{name}"' in text
        bad=subprocess.run(['python3','scripts/import_sparx_mdg.py','--input','tests/mdg-import-invalid/no-uml-profile.xml','--output',str(Path(td)/'bad')],cwd=ROOT,text=True,capture_output=True)
        assert bad.returncode != 0, 'Malformed MDG unexpectedly imported'
        print(json.dumps({'status':'pass','counts':c,'limitations':len(rep.get('limitations',[]))},indent=2))
if __name__=='__main__': main()
