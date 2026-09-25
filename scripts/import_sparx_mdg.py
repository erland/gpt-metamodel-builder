#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, io, json, re, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import yaml

CONNECTOR_TYPES={'Association','Aggregation','Composition','Dependency','Realization','Generalization','Abstraction','InformationFlow','ControlFlow','ObjectFlow','Usage','Trace'}

def slug(s):
    x=re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
    return x or 'unnamed'

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(obj,sort_keys=False,allow_unicode=True),encoding='utf-8')

def decode_shape(value):
    try:
        node=ET.fromstring(value)
        if node.tag!='Image' or node.attrib.get('type')!='EAShapeScript 1.0': return None
        raw=base64.b64decode(node.text or '')
        with zipfile.ZipFile(io.BytesIO(raw),'r') as zf:
            data=zf.read('str.dat')
        return data.decode('utf-16')
    except Exception:
        return None

def profile_sections(root):
    main=root.find('./UMLProfiles/UMLProfile')
    diag=root.find('./DiagramProfile/UMLProfile')
    toolbox=root.find('./UIToolboxes/UMLProfile')
    return main,diag,toolbox

def parse(path:Path):
    root=ET.parse(path).getroot(); doc=root.find('./Documentation')
    main,diagprof,tbprof=profile_sections(root)
    if main is None: raise ValueError('MDG saknar UMLProfiles/UMLProfile')
    pdoc=main.find('./Documentation')
    profile_id=pdoc.attrib.get('name','imported_profile') if pdoc is not None else 'imported_profile'
    tech={k:doc.attrib.get(k,'') for k in ('id','name','version','notes')} if doc is not None else {'id':'imported','name':'Imported MDG','version':'0.0.0','notes':''}
    sts=[]; by_name={}
    for se in main.findall('./Content/Stereotypes/Stereotype'):
        apply=se.find('./AppliesTo/Apply'); uml=apply.attrib.get('type','Class') if apply is not None else 'Class'
        directed=any(p.attrib.get('name')=='direction' for p in se.findall('./AppliesTo/Apply/Property'))
        tags=[dict(t.attrib) for t in se.findall('./TaggedValues/Tag')]
        shape=decode_shape(se.attrib.get('_image','')) if se.attrib.get('_image') else None
        item={'name':se.attrib.get('name',''),'id':slug(se.attrib.get('name','')),'metaclass':uml,'kind':'relationship' if (directed or uml in CONNECTOR_TYPES) else 'element','notes':se.attrib.get('notes',''),'directed':directed,'tags':tags,'shape_script':shape,'quick_links':[]}
        for q in se.findall('./stereotypedrelationships/stereotypedrelationship'):
            item['quick_links'].append({'target_qualified':q.attrib.get('constraint',''),'relationship_qualified':q.attrib.get('stereotype','')})
        sts.append(item); by_name[item['name']]=item
    diagrams=[]
    if diagprof is not None:
        for se in diagprof.findall('./Content/Stereotypes/Stereotype'):
            apply=se.find('./AppliesTo/Apply'); props={p.attrib.get('name'):p.attrib.get('value','') for p in se.findall('./AppliesTo/Apply/Property')}
            diagrams.append({'id':props.get('diagramID') or slug(se.attrib.get('name','')),'name':se.attrib.get('name',''),'metaclass':apply.attrib.get('type','Diagram_Class') if apply is not None else 'Diagram_Class','toolbox_qualified':props.get('toolbox','')})
    toolbox_pages=[]
    if tbprof is not None:
        for se in tbprof.findall('./Content/Stereotypes/Stereotype'):
            tags=[]
            for t in se.findall('./TaggedValues/Tag'):
                n=t.attrib.get('name','')
                if n=='isCollapsed': continue
                m=re.match(r'(?P<profile>[^:]+)::(?P<st>.+?)\(UML::(?P<uml>[^)]+)\)$',n)
                tags.append({'raw':n,'profile':m.group('profile') if m else '', 'stereotype':m.group('st') if m else t.attrib.get('default',''),'uml_type':m.group('uml') if m else ''})
            toolbox_pages.append({'name':se.attrib.get('name',''),'items':tags})
    return {'schema_version':1,'source':{'file':path.name,'format':'sparx_ea_mdg_xml'},'technology':tech,'profile':{'id':profile_id,'name':pdoc.attrib.get('alias',profile_id) if pdoc is not None else profile_id},'stereotypes':sts,'diagrams':diagrams,'toolbox_pages':toolbox_pages}

def project(inter,out:Path):
    tech=inter['technology']; version=tech.get('version') or '0.0.0'; profile=inter['profile']; sts=inter['stereotypes']; by_name={s['name']:s for s in sts}
    # Endpoints from quick linker materialization.
    endpoints={}
    qrules=[]
    for src in sts:
        if src['kind']!='element': continue
        for i,q in enumerate(src['quick_links'],1):
            tgt=q['target_qualified'].split('::')[-1]; rel=q['relationship_qualified'].split('::')[-1]
            if tgt in by_name and rel in by_name:
                endpoints.setdefault(by_name[rel]['id'],{'source':set(),'target':set()})['source'].add(src['id'])
                endpoints[by_name[rel]['id']]['target'].add(by_name[tgt]['id'])
                qrules.append({'id':f"{src['id']}_to_{by_name[tgt]['id']}_{i}",'source':src['id'],'target':by_name[tgt]['id'],'relationship':by_name[rel]['id'],'direction':'source_to_target','label':by_name[rel]['name']})
    elements=[]; rels=[]
    for s in sts:
        if s['kind']=='element': elements.append({'id':s['id'],'name':s['name'],'description':s['notes'],'kind':'structure','property_sets':[f"{s['id']}_properties"] if s['tags'] else []})
        else:
            ep=endpoints.get(s['id'],{'source':set(),'target':set()})
            rels.append({'id':s['id'],'name':s['name'],'kind':slug(s['metaclass']),'directed':bool(s['directed'] or ep['source']),'source':{'types':sorted(ep['source']),'cardinality':'0..*'},'target':{'types':sorted(ep['target']),'cardinality':'0..*'}})
    # Tagged values -> canonical properties. Names are globally deduplicated by signature.
    enum_defs={}; pdefs={}; psets=[]; tvsets=[]
    for s in sts:
        if not s['tags']: continue
        props=[]; tags=[]
        for t in s['tags']:
            base=slug(t.get('name','tag')); pid=base; sig=(t.get('type','char'),t.get('values',''),t.get('default',''))
            if pid in pdefs and pdefs[pid].get('_sig')!=sig: pid=f"{s['id']}_{base}"
            if pid not in pdefs:
                typ=t.get('type','char').lower(); p={'id':pid,'name':t.get('name',pid),'cardinality':'0..1','required':False}
                if typ=='enum':
                    eid=f"{pid}_enum"; vals=[x.strip() for x in t.get('values','').split(',') if x.strip()]; enum_defs[eid]={'id':eid,'name':f"{p['name']} values",'values':[{'id':slug(v),'name':v} for v in vals]}; p['type']={'enumeration':eid}
                elif typ in ('boolean','bool'): p['type']={'builtin':'boolean'}
                elif typ in ('int','integer'): p['type']={'builtin':'integer'}
                elif typ in ('double','number','float'): p['type']={'builtin':'number'}
                else: p['type']={'builtin':'string'}
                if t.get('default','')!='': p['default']=t['default']
                p['_sig']=sig; pdefs[pid]=p
            props.append(pid); tags.append({'property':pid,'tag_name':t.get('name',pid),'render_as':'enum' if t.get('type','').lower()=='enum' else ('memo' if t.get('type')=='Memo' else 'text')})
        setid=f"{s['id']}_properties"; psets.append({'id':setid,'name':f"{s['name']} properties",'properties':props}); tvsets.append({'id':setid,'name':f"{s['name']} properties",'tags':tags})
    for p in pdefs.values(): p.pop('_sig',None)
    mm={'schema_version':1,'metamodel':{'id':slug(tech.get('id') or tech.get('name','imported')),'name':tech.get('name') or 'Imported MDG','version':version,'description':tech.get('notes',''),'namespace':f"imported.{slug(tech.get('id') or 'mdg')}",'default_language':'en'},'elements':elements,'relationships':rels}
    properties={'schema_version':1,'data_types':[],'enumerations':list(enum_defs.values()),'property_definitions':list(pdefs.values()),'property_sets':psets}
    # Viewpoints: preserve diagrams but avoid unsafe inferred allowed content; empty lists are explicit limitations.
    viewpoints={'schema_version':1,'viewpoints':[{'id':d['id'],'name':d['name'],'description':'Imported from Sparx EA diagram profile. Allowed content could not be recovered exactly from MDG XML alone.','allowed_elements':[],'allowed_relationships':[]} for d in inter['diagrams']]}
    notation={'schema_version':1,'styles':[]}
    prov={'schema_version':1,'sources':[{'id':'imported_mdg','name':tech.get('name') or 'Imported MDG','kind':'mdg','notes':f"Reverse engineered from {inter['source']['file']}"}], 'mappings':[{'target':{'kind':s['kind'],'id':s['id']},'source':{'source_id':'imported_mdg','reference':s['name']},'relationship':'imported_from','confidence':1.0} for s in sts]}
    ver={'schema_version':1,'version':{'current':version,'compatibility':{'level':'initial','compatible_with':[]},'changes':[{'type':'add','target':'metamodel','summary':'Reverse engineered from Sparx EA MDG XML.','breaking':False}],'release_notes':'Imported representation; review limitations before treating as semantically complete.'}}
    canonical=out/'canonical'; adapter=out/'platforms'/'sparx-ea'; shapes=adapter/'shapescripts'; shapes.mkdir(parents=True,exist_ok=True)
    for n,o in [('metamodel.yaml',mm),('properties.yaml',properties),('constraints.yaml',{'schema_version':1,'constraints':[]}),('viewpoints.yaml',viewpoints),('guidance.yaml',{'schema_version':1,'guide':{'title':(tech.get('name') or 'Imported MDG')+' – modelleringshandledning','introduction':'Importerad MDG innehåller inte fullständig modelleringshandledning; komplettera denna fil manuellt.','principles':[],'naming_conventions':[]},'elements':[],'relationships':[],'viewpoints':[],'patterns':[],'anti_patterns':[],'faq':[]}),('notation.yaml',notation),('provenance.yaml',prov),('version.yaml',ver)]: dump(canonical/n,o)
    # Reconstructed adapter preserving Sparx fidelity.
    metaclasses=[]; mcmap={}
    for s in sts:
        k='connector' if s['kind']=='relationship' else 'element'; key=(s['metaclass'],k)
        if key not in mcmap:
            mid=f"uml_{slug(s['metaclass'])}"; mcmap[key]=mid; metaclasses.append({'id':mid,'uml_type':s['metaclass'],'kind':k})
    for d in inter['diagrams']:
        key=(d['metaclass'],'diagram')
        if key not in mcmap: mid=f"uml_{slug(d['metaclass'])}"; mcmap[key]=mid; metaclasses.append({'id':mid,'uml_type':d['metaclass'],'kind':'diagram'})
    mapping={'schema_version':1,'technology':{'id':slug(tech.get('id') or tech.get('name','imported')),'name':tech.get('name') or 'Imported MDG','version':version,'description':tech.get('notes',''),'namespace':f"imported.{slug(tech.get('id') or 'mdg')}"},'profile':{'id':profile['id'],'name':profile['name'],'package_name':re.sub(r'\W+','',profile['name']) or 'ImportedProfile'},'files':{'stereotypes':'stereotypes.yaml','tagged_values':'tagged-values.yaml','diagrams':'diagrams.yaml','toolboxes':'toolboxes.yaml','quick_linker':'quick-linker.yaml','shapescripts':'shapescripts.yaml'},'metaclasses':metaclasses}
    stereotypes=[]; shape_specs=[]
    for s in sts:
        z={'id':s['id'],'name':s['name'],'canonical':{'kind':s['kind'],'id':s['id']},'base_metaclass':mcmap[(s['metaclass'],'connector' if s['kind']=='relationship' else 'element')]}
        if s['tags']: z['tagged_value_sets']=[f"{s['id']}_properties"]
        if s['shape_script'] is not None:
            sid=f"{s['id']}_shape"; fn=f"{s['id']}.shape"; (shapes/fn).write_text(s['shape_script'],encoding='utf-8'); z['shape_script']=sid; shape_specs.append({'id':sid,'canonical':{'kind':s['kind'],'id':s['id']},'file':f"shapescripts/{fn}"})
        stereotypes.append(z)
    # toolbox pages preserved as one imported toolbox; raw qualification retained in intermediate.
    pages=[]
    for i,p in enumerate(inter['toolbox_pages'],1):
        items=[]
        for x in p['items']:
            if x['stereotype'] in by_name:
                ref=by_name[x['stereotype']]['id']; items.append({'kind':'relationship' if by_name[x['stereotype']]['kind']=='relationship' else 'stereotype','ref':ref})
        pages.append({'id':f"page_{i}",'name':p['name'],'items':items})
    toolboxes=[{'id':'imported_toolbox','name':'Imported Toolbox','pages':pages}] if pages else []
    diagrams=[{'id':d['id'],'name':d['name'],'viewpoint':d['id'],'base_metaclass':mcmap[(d['metaclass'],'diagram')],'toolbox':'imported_toolbox'} for d in inter['diagrams']] if toolboxes else []
    dump(adapter/'mapping.yaml',mapping); dump(adapter/'stereotypes.yaml',{'schema_version':1,'stereotypes':stereotypes}); dump(adapter/'tagged-values.yaml',{'schema_version':1,'tagged_value_sets':tvsets}); dump(adapter/'diagrams.yaml',{'schema_version':1,'diagrams':diagrams}); dump(adapter/'toolboxes.yaml',{'schema_version':1,'toolboxes':toolboxes}); dump(adapter/'quick-linker.yaml',{'schema_version':1,'rules':qrules}); dump(adapter/'shapescripts.yaml',{'schema_version':1,'scripts':shape_specs})
    limitations=[]
    if inter['diagrams']: limitations.append({'code':'VIEWPOINT_CONTENT_NOT_EXACT','severity':'warning','message':'Diagramprofiler återställdes, men exakt allowed content kan inte härledas säkert från MDG XML.'})
    if inter['toolbox_pages']: limitations.append({'code':'TOOLBOX_GROUPING_APPROXIMATED','severity':'warning','message':'Toolbox-sidor bevaras men gruppering till ursprungliga toolbox-id:n approximeras.'})
    return {'schema_version':1,'technology':tech,'profile':profile,'counts':{'stereotypes':len(sts),'elements':len(elements),'relationships':len(rels),'diagrams':len(inter['diagrams']),'toolbox_pages':len(inter['toolbox_pages']),'quick_linker_rules':len(qrules),'shape_scripts':len(shape_specs)},'limitations':limitations,'intermediate':inter}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output',required=True); ap.add_argument('--json',action='store_true'); a=ap.parse_args()
    inp=Path(a.input).resolve(); out=Path(a.output).resolve(); inter=parse(inp); report=project(inter,out); dump(out/'intermediate'/'mdg-import.yaml',report)
    txt=json.dumps({k:v for k,v in report.items() if k!='intermediate'},ensure_ascii=False,indent=2)
    print(txt if a.json else f"Imported {inp.name}: {report['counts']}")
if __name__=='__main__': main()
