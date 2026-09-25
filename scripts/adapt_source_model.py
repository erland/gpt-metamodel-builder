#!/usr/bin/env python3
from pathlib import Path
import argparse, json, shutil, sys, yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]

def load_yaml(p):
    d=yaml.safe_load(Path(p).read_text(encoding='utf-8'))
    if not isinstance(d,dict): raise ValueError(f'{p} must contain a mapping')
    return d

def dump_yaml(p,d):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True),encoding='utf-8')

def validate_doc(doc,schema_name):
    schema_path=ROOT/'schemas'/schema_name
    schema=json.loads(schema_path.read_text(encoding='utf-8'))
    common=json.loads((ROOT/'schemas'/'common-definitions.schema.json').read_text(encoding='utf-8'))
    registry=Registry().with_resource(common['$id'], Resource.from_contents(common))
    Draft202012Validator(schema,registry=registry,format_checker=FormatChecker()).validate(doc)

def make_proposal(source,target_id,target_name,version):
    return {
      'schema_version':1,'status':'draft',
      'target':{'id':target_id,'name':target_name,'version':version,'description':f'Anpassad metamodell härledd från {source["source"]["name"]}.','default_language':'sv'},
      'element_actions':[{'source_id':x['id'],'action':'keep','target_id':x['id'],'target_name':x['name'],'rationale':'Initialt förslag: behåll begreppet för granskning.'} for x in source.get('elements',[])],
      'relationship_actions':[{'source_id':x['id'],'action':'keep','target_id':x['id'],'target_name':x['name'],'rationale':'Initialt förslag: behåll relationen om dess endpoints behålls.'} for x in source.get('relationships',[])]
    }

def apply(source,plan,out):
    if plan.get('status')!='approved':
        raise ValueError('Adaptation plan must have status=approved before canonical output is created')
    se={x['id']:x for x in source.get('elements',[])}; sr={x['id']:x for x in source.get('relationships',[])}
    element_map={}; elements=[]; prov=[]
    for a in plan['element_actions']:
        if a['source_id'] not in se: raise ValueError(f'Unknown source element {a["source_id"]}')
        if a['action']=='omit': continue
        s=se[a['source_id']]; tid=a.get('target_id') or s['id']; element_map[s['id']]=tid
        elements.append({'id':tid,'name':a.get('target_name') or s['name'],'description':a.get('description',s.get('description','')),'kind':a.get('kind',s.get('kind','custom'))})
        prov.append({'target':{'kind':'element','id':tid},'source':{'source_id':source['source']['id'],'reference':s['reference']},'relationship':'specializes' if a['action']=='specialize' else ('equivalent_to' if a['action']=='keep' else 'derived_from'),'confidence':1.0,'notes':a.get('rationale','')})
    rels=[]
    for a in plan['relationship_actions']:
        if a['source_id'] not in sr: raise ValueError(f'Unknown source relationship {a["source_id"]}')
        if a['action']=='omit': continue
        s=sr[a['source_id']]
        src=[element_map[x] for x in s['source_types'] if x in element_map]; tgt=[element_map[x] for x in s['target_types'] if x in element_map]
        if not src or not tgt: continue
        tid=a.get('target_id') or s['id']
        rels.append({'id':tid,'name':a.get('target_name') or s['name'],'description':a.get('description',s.get('description','')),'kind':a.get('kind',s.get('kind','custom')),'directed':s.get('directed',True),'source':{'types':src,'cardinality':'0..*'},'target':{'types':tgt,'cardinality':'0..*'}})
        prov.append({'target':{'kind':'relationship','id':tid},'source':{'source_id':source['source']['id'],'reference':s['reference']},'relationship':'specializes' if a['action']=='specialize' else ('equivalent_to' if a['action']=='keep' else 'derived_from'),'confidence':1.0,'notes':a.get('rationale','')})
    t=plan['target']; out=Path(out); out.mkdir(parents=True,exist_ok=True)
    dump_yaml(out/'metamodel.yaml',{'schema_version':1,'metamodel':{'id':t['id'],'name':t['name'],'version':t['version'],'description':t.get('description',''),'namespace':t.get('namespace',f'org.example.{t["id"]}'),'default_language':t.get('default_language','sv')},'elements':elements,'relationships':rels})
    dump_yaml(out/'properties.yaml',{'schema_version':1,'data_types':[],'enumerations':[],'property_definitions':[],'property_sets':[]})
    dump_yaml(out/'constraints.yaml',{'schema_version':1,'constraints':[]})
    dump_yaml(out/'viewpoints.yaml',{'schema_version':1,'viewpoints':[]})
    dump_yaml(out/'guidance.yaml',{'schema_version':1,'guide':{'title':t['name']+' – modelleringshandledning','introduction':'','principles':[],'naming_conventions':[]},'elements':[],'relationships':[],'viewpoints':[],'patterns':[],'anti_patterns':[],'faq':[]})
    dump_yaml(out/'notation.yaml',{'schema_version':1,'styles':[]})
    src={k:v for k,v in source['source'].items() if k in {'id','name','kind','version','uri','license_note','notes'}}
    dump_yaml(out/'provenance.yaml',{'schema_version':1,'sources':[src],'mappings':prov})
    dump_yaml(out/'version.yaml',{'schema_version':1,'version':{'current':t['version'],'compatibility':{'level':'initial','compatible_with':[]},'changes':[{'type':'add','target':'metamodel','summary':f'Initial source-based adaptation from {source["source"]["name"]}.','breaking':False}],'release_notes':'Initial source-based adaptation.'}})
    return {'elements':len(elements),'relationships':len(rels),'provenance_mappings':len(prov)}

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('propose'); p.add_argument('source'); p.add_argument('--target-id',required=True); p.add_argument('--target-name',required=True); p.add_argument('--version',default='1.0.0'); p.add_argument('--out',required=True)
    a=sub.add_parser('apply'); a.add_argument('source'); a.add_argument('plan'); a.add_argument('--out',required=True)
    args=ap.parse_args(); source=load_yaml(args.source); validate_doc(source,'source-catalog.schema.json')
    if args.cmd=='propose':
        plan=make_proposal(source,args.target_id,args.target_name,args.version); validate_doc(plan,'adaptation-plan.schema.json'); dump_yaml(args.out,plan); print(json.dumps({'status':'proposal_created','plan':args.out,'requires_approval':True},ensure_ascii=False)); return 0
    plan=load_yaml(args.plan); validate_doc(plan,'adaptation-plan.schema.json'); result=apply(source,plan,args.out); print(json.dumps({'status':'applied',**result},ensure_ascii=False)); return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e:
        print(str(e),file=sys.stderr); raise SystemExit(2)
