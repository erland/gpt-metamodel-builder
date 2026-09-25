#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, io, json, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

DT_NS='urn:schemas-microsoft-com:datatypes'


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding='utf-8'))


def stable_id(text: str) -> str:
    h = hashlib.sha1(text.encode('utf-8')).hexdigest().upper()
    return f"{h[:8]}-{h[8:9]}"


def add_empty_content_tail(content: ET.Element):
    ET.SubElement(content, 'TaggedValueTypes')
    ET.SubElement(content, 'ViewDefinitions')
    ET.SubElement(content, 'Metamodel')


def tag_attributes(prop, render_as, enums):
    attrs = {'name':'','type':'char','description':'','unit':'','values':'','default':''}
    t=prop.get('type',{})
    if 'enumeration' in t:
        enum=enums.get(t['enumeration'],{})
        attrs['type']='enum'; attrs['values']=','.join(v['id'] for v in enum.get('values',[]))
    elif t.get('builtin')=='boolean':
        attrs['type']='boolean'; attrs['values']='true,false'
    elif t.get('builtin') in ('integer','number'):
        attrs['type']='int' if t.get('builtin')=='integer' else 'double'
    if render_as=='memo': attrs['type']='Memo'
    if 'default' in prop:
        attrs['default']=str(prop['default']).lower() if isinstance(prop['default'],bool) else str(prop['default'])
    return attrs


def encode_shape_script(text: str) -> str:
    # EA expects an EAShapeScript payload containing a base64-encoded ZIP with str.dat.
    # Use UTF-16 (with BOM) and fixed ZIP metadata so output is deterministic.
    raw=text.encode('utf-16')
    mem=io.BytesIO()
    info=zipfile.ZipInfo('str.dat', date_time=(1980,1,1,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0
    with zipfile.ZipFile(mem,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zf:
        zf.writestr(info,raw)
    payload=base64.b64encode(mem.getvalue()).decode('ascii')
    return f'<Image type="EAShapeScript 1.0" xmlns:dt="{DT_NS}" dt:dt="bin.base64">{payload}</Image>'


def generate(project_root: Path, canonical: Path, adapter: Path, output: Path):
    mm=load_yaml(canonical/'metamodel.yaml'); props=load_yaml(canonical/'properties.yaml')
    mp=load_yaml(adapter/'mapping.yaml'); sts=load_yaml(adapter/'stereotypes.yaml')['stereotypes']
    tvsets=load_yaml(adapter/'tagged-values.yaml')['tagged_value_sets']; dias=load_yaml(adapter/'diagrams.yaml')['diagrams']
    toolboxes=load_yaml(adapter/'toolboxes.yaml')['toolboxes']; qls=load_yaml(adapter/'quick-linker.yaml')['rules']
    shapes=load_yaml(adapter/'shapescripts.yaml')['scripts']

    technology=mp['technology']; profile=mp['profile']
    metaclasses={x['id']:x for x in mp['metaclasses']}
    prop_defs={x['id']:x for x in props.get('property_definitions',[])}
    enums={x['id']:x for x in props.get('enumerations',[])}
    tv_by={x['id']:x for x in tvsets}; st_by={x['id']:x for x in sts}; shape_by={x['id']:x for x in shapes}

    root=ET.Element('MDG.Technology',{'version':'1.0'})
    ET.SubElement(root,'Documentation',{'id':technology['id'],'name':technology['name'],'version':technology['version'],'notes':technology.get('description','')})

    umlprofiles=ET.SubElement(root,'UMLProfiles')
    up=ET.SubElement(umlprofiles,'UMLProfile',{'profiletype':'uml2'})
    ET.SubElement(up,'Documentation',{'id':stable_id(profile['id']),'name':profile['id'],'alias':profile['name'],'version':technology['version'],'notes':technology.get('description','')})
    content=ET.SubElement(up,'Content'); steroot=ET.SubElement(content,'Stereotypes')

    q_by_source={}
    for q in qls: q_by_source.setdefault(q['source'],[]).append(q)

    embedded=0
    for s in sts:
        c=s['canonical']; canonical_obj=next((x for x in (mm['elements'] if c['kind']=='element' else mm['relationships']) if x['id']==c['id']),{})
        attrs={'name':s['name'],'metatype':s['name'],'notes':canonical_obj.get('description',''),'cx':'90','cy':'70','bgcolor':'-1','fontcolor':'-1','bordercolor':'-1','borderwidth':'1','hideicon':'0'}
        if s.get('shape_script'):
            spec=shape_by[s['shape_script']]
            source=(adapter/spec['file']).read_text(encoding='utf-8')
            attrs['_image']=encode_shape_script(source)
            embedded+=1
        se=ET.SubElement(steroot,'Stereotype',attrs)
        rules=q_by_source.get(s['id'],[])
        if rules:
            sr=ET.SubElement(se,'stereotypedrelationships')
            for q in sorted(rules,key=lambda x:x['id']):
                target=st_by[q['target']]['name']; rel=st_by[q['relationship']]['name']
                ET.SubElement(sr,'stereotypedrelationship',{'constraint':f"{profile['id']}::{target}",'stereotype':f"{profile['id']}::{rel}"})
        applies=ET.SubElement(se,'AppliesTo')
        uml_type=metaclasses[s['base_metaclass']]['uml_type']
        apply=ET.SubElement(applies,'Apply',{'type':uml_type})
        if c['kind']=='relationship' and canonical_obj.get('directed'):
            ET.SubElement(apply,'Property',{'name':'direction','value':'Source -> Destination'})
        else:
            ET.SubElement(apply,'Property',{'name':'isActive','value':''})

        tags=[]
        for set_id in s.get('tagged_value_sets',[]): tags.extend(tv_by[set_id]['tags'])
        if tags:
            tv=ET.SubElement(se,'TaggedValues')
            for t in tags:
                p=prop_defs[t['property']]; a=tag_attributes(p,t.get('render_as'),enums); a['name']=t['tag_name']; a['description']=p.get('description','')
                ET.SubElement(tv,'Tag',a)
    add_empty_content_tail(content)

    root_tvt=ET.SubElement(root,'TaggedValueTypes'); ET.SubElement(root_tvt,'RefData',{'version':'1.0','exporter':'MetamodelBuilder'})

    dp=ET.SubElement(root,'DiagramProfile'); dup=ET.SubElement(dp,'UMLProfile',{'profiletype':'uml2'})
    ET.SubElement(dup,'Documentation',{'id':stable_id(profile['id']+'-diagrams'),'name':profile['id']+'_diagrams','version':technology['version'],'notes':'Generated diagram profile'})
    dcontent=ET.SubElement(dup,'Content'); ds=ET.SubElement(dcontent,'Stereotypes')
    for d in sorted(dias,key=lambda x:x['id']):
        se=ET.SubElement(ds,'Stereotype',{'name':d['name'],'notes':'','cx':'0','cy':'0','bgcolor':'-1','fontcolor':'-1','bordercolor':'-1','borderwidth':'-1','hideicon':'0'})
        apps=ET.SubElement(se,'AppliesTo'); app=ET.SubElement(apps,'Apply',{'type':metaclasses[d['base_metaclass']]['uml_type']})
        ET.SubElement(app,'Property',{'name':'alias','value':d['name']})
        ET.SubElement(app,'Property',{'name':'diagramID','value':d['id']})
        ET.SubElement(app,'Property',{'name':'toolbox','value':f"{profile['id']}_{d['toolbox']}"})
    add_empty_content_tail(dcontent)

    uit=ET.SubElement(root,'UIToolboxes'); tup=ET.SubElement(uit,'UMLProfile',{'profiletype':'uml2'})
    ET.SubElement(tup,'Documentation',{'id':stable_id(profile['id']+'-toolboxes'),'name':profile['id']+'_toolboxes','version':technology['version'],'notes':'Generated toolbox profile'})
    tcontent=ET.SubElement(tup,'Content'); ts=ET.SubElement(tcontent,'Stereotypes')
    for tb in sorted(toolboxes,key=lambda x:x['id']):
        for page in tb['pages']:
            name=f"{tb['name']} - {page['name']}"
            se=ET.SubElement(ts,'Stereotype',{'name':name,'notes':'','cx':'0','cy':'0','bgcolor':'-1','fontcolor':'-1','bordercolor':'-1','borderwidth':'-1','hideicon':'0'})
            apps=ET.SubElement(se,'AppliesTo'); ET.SubElement(apps,'Apply',{'type':'ToolboxPage'})
            tv=ET.SubElement(se,'TaggedValues'); ET.SubElement(tv,'Tag',{'name':'isCollapsed','type':'bool','description':'','unit':'','values':'true,false','default':'true'})
            for item in page['items']:
                st=st_by[item['ref']]; mc=metaclasses[st['base_metaclass']]['uml_type']
                ET.SubElement(tv,'Tag',{'name':f"{profile['id']}::{st['name']}(UML::{mc})",'type':'','description':'','unit':'','values':'','default':st['name']})
    add_empty_content_tail(tcontent)

    ET.indent(root,space='  ')
    output.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=True,short_empty_elements=True)
    return {'output':str(output),'technology':technology['id'],'version':technology['version'],'stereotypes':len(sts),'diagrams':len(dias),'toolboxes':len(toolboxes),'quick_linker_rules':len(qls),'shape_scripts_embedded':embedded}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root',default='.')
    ap.add_argument('--canonical',required=True); ap.add_argument('--adapter',required=True); ap.add_argument('--output',required=True); ap.add_argument('--json',action='store_true')
    a=ap.parse_args(); r=generate(Path(a.project_root).resolve(),Path(a.canonical).resolve(),Path(a.adapter).resolve(),Path(a.output).resolve())
    print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else f"Generated {r['output']} ({r['stereotypes']} stereotypes, {r['shape_scripts_embedded']} shape scripts)")
    return 0
if __name__=='__main__': raise SystemExit(main())
