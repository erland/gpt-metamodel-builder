#!/usr/bin/env python3
from pathlib import Path
import copy, json, shutil, subprocess, tempfile, yaml
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'examples/architecture-lite'

def load(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def dump(p,d): p.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True),encoding='utf-8')
def run(old,new,*extra): return subprocess.run(['python3','scripts/diff_metamodel.py',str(old),str(new),*extra],cwd=ROOT,text=True,capture_output=True)

def clone(dst): shutil.copytree(SRC,dst)

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); old=td/'old'; clone(old)
        # Backward-compatible additive release.
        minor=td/'minor'; clone(minor)
        mm=load(minor/'metamodel.yaml'); mm['elements'].append({'id':'platform_service','name':'Platform Service','description':'A platform-provided service.','kind':'behavior','property_sets':['lifecycle']}); dump(minor/'metamodel.yaml',mm)
        v=load(minor/'version.yaml'); v['version']['current']='1.1.0'; v['version']['previous']='1.0.0'; v['version']['compatibility']={'level':'backward_compatible','compatible_with':['1.0.0']}; dump(minor/'version.yaml',v)
        outj=td/'minor.json'; outr=td/'minor-release.md'; outm=td/'minor-migration.md'
        p=run(old,minor,'--json',str(outj),'--release-notes',str(outr),'--migration-notes',str(outm)); assert p.returncode==0,p.stdout+p.stderr
        rep=json.loads(outj.read_text()); assert rep['recommended_bump']=='minor' and rep['summary']['breaking']==0 and rep['declared_version_sufficient']
        assert 'platform_service' in outr.read_text()
        # Breaking release.
        major=td/'major'; clone(major)
        mm=load(major/'metamodel.yaml'); mm['elements']=[x for x in mm['elements'] if x['id']!='platform']; mm['relationships']=[x for x in mm['relationships'] if x['id']!='platform_supports_application']; dump(major/'metamodel.yaml',mm)
        views=load(major/'viewpoints.yaml'); views['viewpoints']=[v for v in views['viewpoints'] if v['id']!='application_platform']; dump(major/'viewpoints.yaml',views)
        notation=load(major/'notation.yaml'); notation['styles']=[s for s in notation['styles'] if s.get('applies_to',{}).get('type')!='platform_supports_application']; dump(major/'notation.yaml',notation)
        v=load(major/'version.yaml'); v['version']['current']='2.0.0'; v['version']['previous']='1.0.0'; v['version']['compatibility']={'level':'breaking','compatible_with':[]}; dump(major/'version.yaml',v)
        outj2=td/'major.json'; p=run(old,major,'--json',str(outj2)); assert p.returncode==0,p.stdout+p.stderr
        rep2=json.loads(outj2.read_text()); assert rep2['recommended_bump']=='major' and rep2['summary']['breaking']>=2 and rep2['declared_version_sufficient']
        # Insufficient version bump must fail.
        bad=td/'bad'; shutil.copytree(major,bad); v=load(bad/'version.yaml'); v['version']['current']='1.1.0'; dump(bad/'version.yaml',v)
        p=run(old,bad); assert p.returncode==2,'Breaking change with minor bump unexpectedly accepted'
        print(json.dumps({'status':'pass','minor_changes':rep['summary'],'major_changes':rep2['summary']},indent=2))
if __name__=='__main__': main()
