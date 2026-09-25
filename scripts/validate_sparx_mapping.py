#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

SCHEMAS={
 'mapping.yaml':'sparx-ea-mapping.schema.json','stereotypes.yaml':'sparx-ea-stereotypes.schema.json','tagged-values.yaml':'sparx-ea-tagged-values.schema.json',
 'diagrams.yaml':'sparx-ea-diagrams.schema.json','toolboxes.yaml':'sparx-ea-toolboxes.schema.json','quick-linker.yaml':'sparx-ea-quick-linker.schema.json','shapescripts.yaml':'sparx-ea-shapescripts.schema.json'}

def load(path):
    return yaml.safe_load(path.read_text(encoding='utf-8'))

def ids(items): return {x['id'] for x in items}

def validate(root:Path, canonical:Path, adapter:Path):
    findings=[]
    data={}
    for fname,sname in SCHEMAS.items():
        p=adapter/fname
        if not p.is_file():
            findings.append({'code':'EA001','severity':'error','message':f'Missing adapter file: {fname}'})
            continue
        try:
            obj=load(p); data[fname]=obj
            schema=json.loads((root/'schemas'/sname).read_text(encoding='utf-8'))
            for e in Draft202012Validator(schema).iter_errors(obj):
                findings.append({'code':'EA002','severity':'error','message':f'{fname}: {e.message}'})
        except Exception as e:
            findings.append({'code':'EA003','severity':'error','message':f'{fname}: {e}'})
    if findings: return report(findings)

    mm=load(canonical/'metamodel.yaml'); props=load(canonical/'properties.yaml'); views=load(canonical/'viewpoints.yaml')
    elem={x['id']:x for x in mm.get('elements',[])}; rel={x['id']:x for x in mm.get('relationships',[])}
    prop_ids=ids(props.get('property_definitions',[])); pset_ids=ids(props.get('property_sets',[])); view_ids=ids(views.get('viewpoints',[]))
    mp=data['mapping.yaml']; sts=data['stereotypes.yaml']['stereotypes']; tvs=data['tagged-values.yaml']['tagged_value_sets']; dias=data['diagrams.yaml']['diagrams']; tbs=data['toolboxes.yaml']['toolboxes']; ql=data['quick-linker.yaml']['rules']; ss=data['shapescripts.yaml']['scripts']
    mc={x['id']:x for x in mp['metaclasses']}; st_by={x['id']:x for x in sts}; tv_ids=ids(tvs); tb_ids=ids(tbs); ss_ids=ids(ss)

    if mp['technology']['version'] != mm['metamodel']['version']:
        findings.append({'code':'EA100','severity':'error','message':'Technology version must equal canonical metamodel version'})

    seen=set()
    for s in sts:
        if s['id'] in seen: findings.append({'code':'EA110','severity':'error','message':f'Duplicate stereotype id: {s["id"]}'})
        seen.add(s['id'])
        c=s['canonical']; universe=elem if c['kind']=='element' else rel
        if c['id'] not in universe: findings.append({'code':'EA111','severity':'error','message':f'Stereotype {s["id"]} references unknown canonical {c["kind"]}: {c["id"]}'})
        m=mc.get(s['base_metaclass'])
        expected='element' if c['kind']=='element' else 'connector'
        if not m: findings.append({'code':'EA112','severity':'error','message':f'Stereotype {s["id"]} references unknown metaclass: {s["base_metaclass"]}'})
        elif m['kind'] != expected: findings.append({'code':'EA113','severity':'error','message':f'Stereotype {s["id"]} requires {expected} metaclass, got {m["kind"]}'})
        for tv in s.get('tagged_value_sets',[]):
            if tv not in tv_ids: findings.append({'code':'EA114','severity':'error','message':f'Stereotype {s["id"]} references unknown tagged value set: {tv}'})
        if 'shape_script' in s and s['shape_script'] not in ss_ids:
            findings.append({'code':'EA115','severity':'error','message':f'Stereotype {s["id"]} references unknown Shape Script: {s["shape_script"]}'})

    for tvset in tvs:
        for tag in tvset['tags']:
            if tag['property'] not in prop_ids: findings.append({'code':'EA120','severity':'error','message':f'Tagged value set {tvset["id"]} references unknown property: {tag["property"]}'})

    for d in dias:
        if d['viewpoint'] not in view_ids: findings.append({'code':'EA130','severity':'error','message':f'Diagram {d["id"]} references unknown viewpoint: {d["viewpoint"]}'})
        m=mc.get(d['base_metaclass'])
        if not m or m['kind']!='diagram': findings.append({'code':'EA131','severity':'error','message':f'Diagram {d["id"]} requires a declared diagram metaclass'})
        if d['toolbox'] not in tb_ids: findings.append({'code':'EA132','severity':'error','message':f'Diagram {d["id"]} references unknown toolbox: {d["toolbox"]}'})

    relation_stereotypes={s['id'] for s in sts if s['canonical']['kind']=='relationship'}
    element_stereotypes={s['id'] for s in sts if s['canonical']['kind']=='element'}
    for tb in tbs:
        for page in tb['pages']:
            for item in page['items']:
                expected=element_stereotypes if item['kind']=='stereotype' else relation_stereotypes
                if item['ref'] not in expected: findings.append({'code':'EA140','severity':'error','message':f'Toolbox {tb["id"]} references unknown/incompatible {item["kind"]}: {item["ref"]}'})

    # map canonical element id -> stereotype id and canonical relationship id -> stereotype id; v1 expects identity not required
    elem_st={s['canonical']['id']:s['id'] for s in sts if s['canonical']['kind']=='element'}
    rel_st={s['canonical']['id']:s['id'] for s in sts if s['canonical']['kind']=='relationship'}
    st_to_elem={v:k for k,v in elem_st.items()}; st_to_rel={v:k for k,v in rel_st.items()}
    for q in ql:
        if q['source'] not in element_stereotypes or q['target'] not in element_stereotypes:
            findings.append({'code':'EA150','severity':'error','message':f'Quick Linker {q["id"]} references unknown endpoint stereotype'})
            continue
        if q['relationship'] not in relation_stereotypes:
            findings.append({'code':'EA151','severity':'error','message':f'Quick Linker {q["id"]} references unknown relationship stereotype'})
            continue
        cr=rel.get(st_to_rel[q['relationship']]); src=st_to_elem[q['source']]; tgt=st_to_elem[q['target']]
        if q.get('direction','source_to_target')=='source_to_target':
            ok=src in cr['source']['types'] and tgt in cr['target']['types']
        elif q.get('direction')=='target_to_source':
            ok=tgt in cr['source']['types'] and src in cr['target']['types']
        else:
            ok=(src in cr['source']['types'] and tgt in cr['target']['types']) or (tgt in cr['source']['types'] and src in cr['target']['types'])
        if not ok: findings.append({'code':'EA152','severity':'error','message':f'Quick Linker {q["id"]} contradicts canonical relationship endpoints'})

    for s in ss:
        c=s['canonical']; universe=elem if c['kind']=='element' else rel
        if c['id'] not in universe: findings.append({'code':'EA160','severity':'error','message':f'Shape Script {s["id"]} references unknown canonical object: {c["id"]}'})
        if not (adapter/s['file']).is_file(): findings.append({'code':'EA161','severity':'error','message':f'Shape Script file missing: {s["file"]}'})

    # Leakage guard: canonical files must not contain Sparx-adapter keys.
    forbidden={'sparx','sparx_ea','uml_metaclass','tagged_value','quick_linker','shape_script','toolbox_profile','diagram_profile'}
    for fname in ['metamodel.yaml','properties.yaml','constraints.yaml','viewpoints.yaml','notation.yaml','provenance.yaml','version.yaml']:
        text=(canonical/fname).read_text(encoding='utf-8').lower()
        for token in forbidden:
            if token+':' in text:
                findings.append({'code':'EA170','severity':'error','message':f'Platform-specific key leaked into canonical file {fname}: {token}'})
    return report(findings)

def report(findings):
    errors=sum(1 for f in findings if f['severity']=='error')
    return {'result':'pass' if errors==0 else 'fail','summary':{'errors':errors,'findings':len(findings)},'findings':findings}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.'); ap.add_argument('--canonical',required=True); ap.add_argument('--adapter',required=True); ap.add_argument('--json',action='store_true')
    a=ap.parse_args(); root=Path(a.project_root).resolve(); r=validate(root,Path(a.canonical).resolve(),Path(a.adapter).resolve())
    print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else f"Sparx mapping validation: {r['result'].upper()} ({r['summary']['errors']} errors)")
    return 0 if r['result']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
