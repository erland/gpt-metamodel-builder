#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, io, json, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

DT='{urn:schemas-microsoft-com:datatypes}dt'

def load(p): return yaml.safe_load(p.read_text(encoding='utf-8'))

def decode_shape_envelope(value):
    try:
        image=ET.fromstring(value)
        if image.tag!='Image' or image.get('type')!='EAShapeScript 1.0' or image.get(DT)!='bin.base64':
            raise ValueError('invalid EAShapeScript envelope')
        data=base64.b64decode((image.text or '').encode('ascii'),validate=True)
        with zipfile.ZipFile(io.BytesIO(data),'r') as zf:
            if zf.namelist()!=['str.dat']:
                raise ValueError(f'expected only str.dat, got {zf.namelist()}')
            raw=zf.read('str.dat')
        return raw.decode('utf-16')
    except Exception as e:
        raise ValueError(str(e))

def simple_shape_sanity(source):
    stripped=[]; i=0
    # coarse deterministic sanity: balance braces outside quoted strings
    depth=0; in_str=False; esc=False
    for ch in source:
        if in_str:
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch=='"': in_str=False
            continue
        if ch=='"': in_str=True
        elif ch=='{': depth+=1
        elif ch=='}':
            depth-=1
            if depth<0: return False
    return not in_str and depth==0 and ('shape ' in source.lower() or 'decoration ' in source.lower())

def validate(xml_path, canonical, adapter):
    f=[]
    try: root=ET.parse(xml_path).getroot()
    except Exception as e: return {'result':'fail','summary':{'errors':1,'findings':1},'findings':[{'code':'MDG001','severity':'error','message':str(e)}]}
    if root.tag!='MDG.Technology': f.append({'code':'MDG002','severity':'error','message':'Root must be MDG.Technology'})
    doc=root.find('Documentation'); mp=load(Path(adapter)/'mapping.yaml'); st=load(Path(adapter)/'stereotypes.yaml')['stereotypes']; d=load(Path(adapter)/'diagrams.yaml')['diagrams']; tb=load(Path(adapter)/'toolboxes.yaml')['toolboxes']; tvsets=load(Path(adapter)/'tagged-values.yaml')['tagged_value_sets']; ql=load(Path(adapter)/'quick-linker.yaml')['rules']; shapes=load(Path(adapter)/'shapescripts.yaml')['scripts']
    tech=mp['technology']; profile=mp['profile']
    if doc is None or doc.get('id')!=tech['id'] or doc.get('version')!=tech['version']: f.append({'code':'MDG003','severity':'error','message':'Technology Documentation mismatch'})
    allowed_root={'Documentation','UMLProfiles','TaggedValueTypes','DiagramProfile','UIToolboxes'}
    extra=[x.tag for x in root if x.tag not in allowed_root]
    if extra: f.append({'code':'MDG004','severity':'error','message':f'Unexpected MDG root sections: {extra}'})

    uml=root.find('UMLProfiles/UMLProfile/Content/Stereotypes'); generated=[] if uml is None else uml.findall('Stereotype')
    if len(generated)!=len(st): f.append({'code':'MDG010','severity':'error','message':f'Expected {len(st)} stereotypes, got {len(generated)}'})
    names={x.get('name') for x in generated}; expected={x['name'] for x in st}
    if names!=expected: f.append({'code':'MDG011','severity':'error','message':'Generated stereotype names do not match adapter'})
    byname={x.get('name'):x for x in generated}; mcs={x['id']:x['uml_type'] for x in mp['metaclasses']}
    for s in st:
        se=byname.get(s['name']); app=None if se is None else se.find('AppliesTo/Apply')
        if app is None or app.get('type')!=mcs[s['base_metaclass']]: f.append({'code':'MDG040','severity':'error','message':f'Wrong/missing AppliesTo for {s["id"]}'})

    # Shape scripts must be embedded in EA's EAShapeScript envelope and round-trip exactly.
    shape_by={x['id']:x for x in shapes}
    embedded=0
    for s in st:
        if not s.get('shape_script'): continue
        se=byname.get(s['name']); value=None if se is None else se.get('_image')
        if not value:
            f.append({'code':'MDG050','severity':'error','message':f'Missing _image Shape Script for {s["id"]}'})
            continue
        try:
            decoded=decode_shape_envelope(value); spec=shape_by[s['shape_script']]; expected_text=(Path(adapter)/spec['file']).read_text(encoding='utf-8')
            if decoded!=expected_text: f.append({'code':'MDG051','severity':'error','message':f'Shape Script round-trip mismatch for {s["id"]}'})
            if not simple_shape_sanity(decoded): f.append({'code':'MDG052','severity':'error','message':f'Shape Script basic syntax sanity failed for {s["id"]}'})
            embedded+=1
        except Exception as e:
            f.append({'code':'MDG053','severity':'error','message':f'Invalid EAShapeScript payload for {s["id"]}: {e}'})

    diagram_nodes=root.findall('DiagramProfile/UMLProfile/Content/Stereotypes/Stereotype')
    if len(diagram_nodes)!=len(d): f.append({'code':'MDG020','severity':'error','message':'Diagram profile count mismatch'})
    expected_pages=sum(len(x['pages']) for x in tb); toolbox_nodes=root.findall('UIToolboxes/UMLProfile/Content/Stereotypes/Stereotype')
    if len(toolbox_nodes)!=expected_pages: f.append({'code':'MDG030','severity':'error','message':'Toolbox page count mismatch'})

    # Diagram toolbox properties must reference generated toolbox profile identifiers.
    expected_toolboxes={f"{profile['id']}_{x['id']}" for x in tb}
    for node in diagram_nodes:
        prop=node.find("AppliesTo/Apply/Property[@name='toolbox']")
        if prop is None or prop.get('value') not in expected_toolboxes:
            f.append({'code':'MDG021','severity':'error','message':f'Diagram {node.get("name")} has invalid toolbox reference'})

    # Inline tags: verify every declared adapter tag appears on stereotypes using that set.
    tv_by={x['id']:x for x in tvsets}
    st_by_id={x['id']:x for x in st}
    for spec in st:
        se=byname.get(spec['name'])
        if se is None: continue
        actual={x.get('name') for x in se.findall('TaggedValues/Tag')}
        expected_tags=set()
        for set_id in spec.get('tagged_value_sets',[]): expected_tags.update(x['tag_name'] for x in tv_by[set_id]['tags'])
        if not expected_tags.issubset(actual): f.append({'code':'MDG060','severity':'error','message':f'Missing Tagged Values for {spec["id"]}: {sorted(expected_tags-actual)}'})

    # Quick Linker equivalent must be materialized as stereotypedrelationships.
    q_by={}
    for x in ql: q_by.setdefault(x['source'],[]).append(x)
    for src,rules in q_by.items():
        se=byname.get(st_by_id[src]['name']); actual=set()
        if se is not None:
            for rel in se.findall('stereotypedrelationships/stereotypedrelationship'):
                actual.add((rel.get('constraint'),rel.get('stereotype')))
        expected_pairs={(f"{profile['id']}::{st_by_id[x['target']]['name']}",f"{profile['id']}::{st_by_id[x['relationship']]['name']}") for x in rules}
        if actual!=expected_pairs: f.append({'code':'MDG070','severity':'error','message':f'Quick Linker relationship set mismatch for {src}'})

    errors=sum(x['severity']=='error' for x in f)
    return {'result':'pass' if errors==0 else 'fail','summary':{'errors':errors,'findings':len(f),'shape_scripts_embedded':embedded},'findings':f}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--xml',required=True); ap.add_argument('--canonical',required=True); ap.add_argument('--adapter',required=True); ap.add_argument('--json',action='store_true')
    a=ap.parse_args(); r=validate(Path(a.xml),Path(a.canonical),Path(a.adapter)); print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else f"Generated MDG validation: {r['result'].upper()} ({r['summary']['errors']} errors)"); return 0 if r['result']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
