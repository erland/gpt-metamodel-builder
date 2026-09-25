#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any
import yaml

FILES=['metamodel.yaml','properties.yaml','constraints.yaml','viewpoints.yaml','guidance.yaml','notation.yaml','provenance.yaml','version.yaml']

def load(p:Path)->dict[str,Any]:
    d=yaml.safe_load(p.read_text(encoding='utf-8'))
    if not isinstance(d,dict): raise ValueError(f'{p}: expected mapping')
    return d

def by_id(items): return {x['id']:x for x in items if isinstance(x,dict) and 'id' in x}
def norm(x): return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def semver(v:str):
    m=re.fullmatch(r'(\d+)\.(\d+)\.(\d+)',v)
    if not m: raise ValueError(f'Invalid semver: {v}')
    return tuple(map(int,m.groups()))
def bump(v:str,kind:str):
    a,b,c=semver(v)
    return f'{a+1}.0.0' if kind=='major' else f'{a}.{b+1}.0' if kind=='minor' else f'{a}.{b}.{c+1}'

def add(changes, category, ident, change, severity, summary, details=None):
    changes.append({'category':category,'id':ident,'change':change,'severity':severity,'summary':summary,**({'details':details} if details else {})})

def compare_collection(changes, category, old_items, new_items, removal='breaking', addition='non_breaking'):
    old,new=by_id(old_items),by_id(new_items)
    for ident in sorted(old.keys()-new.keys()): add(changes,category,ident,'remove',removal,f'Removed {category[:-1] if category.endswith("s") else category} {ident}')
    for ident in sorted(new.keys()-old.keys()): add(changes,category,ident,'add',addition,f'Added {category[:-1] if category.endswith("s") else category} {ident}')
    return old,new

def compare(old_dir:Path,new_dir:Path):
    od={f:load(old_dir/f) for f in FILES}; nd={f:load(new_dir/f) for f in FILES}
    changes=[]
    oe,ne=compare_collection(changes,'elements',od['metamodel.yaml'].get('elements',[]),nd['metamodel.yaml'].get('elements',[]))
    orl,nrl=compare_collection(changes,'relationships',od['metamodel.yaml'].get('relationships',[]),nd['metamodel.yaml'].get('relationships',[]))
    opd,npd=compare_collection(changes,'properties',od['properties.yaml'].get('property_definitions',[]),nd['properties.yaml'].get('property_definitions',[]))
    ops,nps=compare_collection(changes,'property_sets',od['properties.yaml'].get('property_sets',[]),nd['properties.yaml'].get('property_sets',[]))
    oen,nen=compare_collection(changes,'enumerations',od['properties.yaml'].get('enumerations',[]),nd['properties.yaml'].get('enumerations',[]))
    oc,nc=compare_collection(changes,'constraints',od['constraints.yaml'].get('constraints',[]),nd['constraints.yaml'].get('constraints',[]),removal='non_breaking')
    ov,nv=compare_collection(changes,'viewpoints',od['viewpoints.yaml'].get('viewpoints',[]),nd['viewpoints.yaml'].get('viewpoints',[]),removal='potentially_breaking')
    on,nn=compare_collection(changes,'notation',od['notation.yaml'].get('styles',[]),nd['notation.yaml'].get('styles',[]),removal='non_breaking')

    for ident in sorted(oe.keys()&ne.keys()):
        a,b=oe[ident],ne[ident]
        for key,severity in [('name','non_breaking'),('kind','breaking'),('extends','potentially_breaking'),('property_sets','potentially_breaking')]:
            if norm(a.get(key))!=norm(b.get(key)): add(changes,'elements',ident,'change',severity,f'Element {ident}: {key} changed',{'old':a.get(key),'new':b.get(key)})
    for ident in sorted(orl.keys()&nrl.keys()):
        a,b=orl[ident],nrl[ident]
        for key,severity in [('name','non_breaking'),('kind','potentially_breaking'),('directed','breaking'),('source','breaking'),('target','breaking'),('extends','potentially_breaking'),('property_sets','potentially_breaking')]:
            if norm(a.get(key))!=norm(b.get(key)): add(changes,'relationships',ident,'change',severity,f'Relationship {ident}: {key} changed',{'old':a.get(key),'new':b.get(key)})
    for ident in sorted(opd.keys()&npd.keys()):
        a,b=opd[ident],npd[ident]
        for key,severity in [('name','non_breaking'),('type','breaking'),('cardinality','potentially_breaking'),('required','breaking'),('default','potentially_breaking')]:
            if norm(a.get(key))!=norm(b.get(key)): add(changes,'properties',ident,'change',severity,f'Property {ident}: {key} changed',{'old':a.get(key),'new':b.get(key)})
    for ident in sorted(oen.keys()&nen.keys()):
        a,b=oen[ident],nen[ident]
        av,bv=by_id(a.get('values',[])),by_id(b.get('values',[]))
        for val in sorted(av.keys()-bv.keys()): add(changes,'enumeration_values',f'{ident}.{val}','remove','breaking',f'Removed enumeration value {ident}.{val}')
        for val in sorted(bv.keys()-av.keys()): add(changes,'enumeration_values',f'{ident}.{val}','add','non_breaking',f'Added enumeration value {ident}.{val}')
    for ident in sorted(ops.keys()&nps.keys()):
        if norm(ops[ident].get('properties'))!=norm(nps[ident].get('properties')): add(changes,'property_sets',ident,'change','potentially_breaking',f'Property set {ident}: membership changed',{'old':ops[ident].get('properties'),'new':nps[ident].get('properties')})
    for ident in sorted(oc.keys()&nc.keys()):
        if norm(oc[ident])!=norm(nc[ident]): add(changes,'constraints',ident,'change','potentially_breaking',f'Constraint {ident} changed')
    for ident in sorted(ov.keys()&nv.keys()):
        if norm(ov[ident])!=norm(nv[ident]): add(changes,'viewpoints',ident,'change','potentially_breaking',f'Viewpoint {ident} changed')
    for ident in sorted(on.keys()&nn.keys()):
        if norm(on[ident])!=norm(nn[ident]): add(changes,'notation',ident,'change','non_breaking',f'Notation style {ident} changed')

    # provenance is traceability-only; report changes without compatibility impact
    if norm(od['provenance.yaml'])!=norm(nd['provenance.yaml']): add(changes,'provenance','provenance','change','non_breaking','Provenance changed')

    oldv=od['version.yaml']['version']['current']; newv=nd['version.yaml']['version']['current']
    severity_counts={k:sum(1 for c in changes if c['severity']==k) for k in ['breaking','potentially_breaking','non_breaking']}
    if severity_counts['breaking']:
        recommended='major'; compatibility='breaking'
    elif changes:
        recommended='minor' if any(c['change']=='add' or c['severity']=='potentially_breaking' for c in changes) else 'patch'; compatibility='backward_compatible'
    else:
        recommended='patch'; compatibility='backward_compatible'
    expected=bump(oldv,recommended)
    actual_delta=semver(newv)
    version_ok=(recommended=='major' and actual_delta[0]>semver(oldv)[0]) or (recommended=='minor' and (actual_delta[0]>semver(oldv)[0] or (actual_delta[0]==semver(oldv)[0] and actual_delta[1]>semver(oldv)[1]))) or (recommended=='patch' and actual_delta>semver(oldv))
    return {'tool':'metamodel-builder-diff-v1','old_version':oldv,'new_version':newv,'summary':{'changes':len(changes),**severity_counts},'compatibility':compatibility,'recommended_bump':recommended,'minimum_recommended_version':expected,'declared_version_sufficient':version_ok,'changes':changes}

def markdown(report):
    lines=[f"# Metamodelländringar {report['old_version']} → {report['new_version']}",'',f"Kompatibilitet: **{report['compatibility']}**",f"Rekommenderad versionshöjning: **{report['recommended_bump']}** (minst {report['minimum_recommended_version']})",f"Deklarerad version tillräcklig: **{'ja' if report['declared_version_sufficient'] else 'nej'}**",'', '## Sammanfattning','',f"- Breaking: {report['summary']['breaking']}",f"- Potentiellt breaking: {report['summary']['potentially_breaking']}",f"- Icke-breaking: {report['summary']['non_breaking']}",'','## Ändringar','']
    if not report['changes']: lines.append('Inga semantiska ändringar identifierades.')
    for c in report['changes']: lines.append(f"- **{c['severity']}** – {c['summary']}")
    return '\n'.join(lines)+'\n'

def migration(report):
    relevant=[c for c in report['changes'] if c['severity'] in ('breaking','potentially_breaking')]
    lines=[f"# Migrationsnoteringar {report['old_version']} → {report['new_version']}",'']
    if not relevant: lines.append('Ingen särskild modellmigration bedöms nödvändig utifrån den semantiska diffen.')
    else:
        lines.append('Granska följande före uppgradering:'); lines.append('')
        for c in relevant: lines.append(f"- {c['summary']} ({c['severity']})")
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('old'); ap.add_argument('new'); ap.add_argument('--json'); ap.add_argument('--release-notes'); ap.add_argument('--migration-notes')
    a=ap.parse_args(); rep=compare(Path(a.old),Path(a.new))
    if a.json: Path(a.json).write_text(json.dumps(rep,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if a.release_notes: Path(a.release_notes).write_text(markdown(rep),encoding='utf-8')
    if a.migration_notes: Path(a.migration_notes).write_text(migration(rep),encoding='utf-8')
    print(json.dumps(rep,ensure_ascii=False,indent=2))
    return 0 if rep['declared_version_sufficient'] else 2
if __name__=='__main__': raise SystemExit(main())
