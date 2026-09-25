#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path
from typing import Any
import yaml

FILES=["metamodel.yaml","properties.yaml","constraints.yaml","viewpoints.yaml","guidance.yaml","notation.yaml","provenance.yaml","version.yaml"]

def load_yaml(p:Path)->dict[str,Any]:
    d=yaml.safe_load(p.read_text(encoding="utf-8"));
    if not isinstance(d,dict): raise ValueError(f"{p}: expected mapping")
    return d

def esc_md(s): return str(s).replace('|','\\|')
def md_table(headers,rows):
    out=['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']
    for row in rows: out.append('| '+' | '.join(esc_md(', '.join(map(str,x)) if isinstance(x,list) else (x if x is not None else '')) for x in row)+' |')
    return '\n'.join(out)
def bullets(items): return '\n'.join(f'- {x}' for x in (items or [])) or '- -'
def heading(title,level=2): return '#'*level+' '+title

def model_docs(model_dir:Path):
    d={n:load_yaml(model_dir/n) for n in FILES}; mm=d['metamodel.yaml']; g=d['guidance.yaml']; views=d['viewpoints.yaml']; props=d['properties.yaml']; cons=d['constraints.yaml']; ver=d['version.yaml']; prov=d['provenance.yaml']
    meta=mm['metamodel']; elem={e['id']:e for e in mm.get('elements',[])}; rel={r['id']:r for r in mm.get('relationships',[])}; vp={v['id']:v for v in views.get('viewpoints',[])}
    # reference
    r=[f"# {meta['name']} – metamodellreferens",'',meta.get('description',''),'',heading('Elementtyper'),'',md_table(['Namn','ID','Beskrivning'],[[e.get('name'),e.get('id'),e.get('description','')] for e in mm.get('elements',[])]),'',heading('Relationstyper'),'',md_table(['Namn','ID','Källa','Mål'],[[x.get('name'),x.get('id'),x.get('source',{}).get('types',[]),x.get('target',{}).get('types',[])] for x in mm.get('relationships',[])]),'',heading('Properties'),'',md_table(['Namn','ID','Kardinalitet','Obligatorisk'],[[x.get('name'),x.get('id'),x.get('cardinality',''),x.get('required',False)] for x in props.get('property_definitions',[])]),'',heading('Constraints'),'',md_table(['Namn','ID','Severity','Meddelande'],[[x.get('name'),x.get('id'),x.get('severity'),x.get('message')] for x in cons.get('constraints',[])]),'',heading('Viewpoints'),'']
    for x in views.get('viewpoints',[]): r += [heading(f"{x.get('name')} (`{x.get('id')}`)",3),'',x.get('description',''),'',f"**Syfte:** {x.get('purpose','')}",'']
    r += [heading('Provenance'),'',md_table(['Källa','Typ','Notering'],[[x.get('name'),x.get('kind'),x.get('notes','')] for x in prov.get('sources',[])]),'',heading('Version'),'',f"Aktuell version: **{ver.get('version',{}).get('current','')}**",'']

    # modeling guide
    guide=[f"# {g.get('guide',{}).get('title',meta['name']+' – modelleringshandledning')}",'',g.get('guide',{}).get('introduction',''),'',heading('Grundprinciper'),'',bullets(g.get('guide',{}).get('principles',[])),'',heading('Namngivning'),'',bullets(g.get('guide',{}).get('naming_conventions',[])),'',heading('Objektguide'),'']
    for x in g.get('elements',[]):
        e=elem.get(x.get('type'),{}); guide += [heading(f"{e.get('name',x.get('type'))} (`{x.get('type')}`)",3),'',x.get('purpose',''),'', '**Använd när**','',bullets(x.get('use_when',[])),'','**Använd inte när**','',bullets(x.get('do_not_use_when',[])),'']
        n=x.get('naming',{}); guide += ['**Namngivning**','',n.get('recommendation',''),'',f"Bra exempel: {', '.join(n.get('good_examples',[])) or '-'}",f"Dåliga exempel: {', '.join(n.get('bad_examples',[])) or '-'}",'','**Vanliga misstag**','',bullets(x.get('common_mistakes',[])),'']
    guide += [heading('Relationsguide'),'']
    for x in g.get('relationships',[]):
        rr=rel.get(x.get('type'),{}); guide += [heading(f"{rr.get('name',x.get('type'))} (`{x.get('type')}`)",3),'',x.get('meaning',''),'', '**Använd när**','',bullets(x.get('use_when',[])),'','**Undvik när**','',bullets(x.get('avoid_when',[])),'']
        for ex in x.get('examples',[]): guide += [f"Exempel: **{ex.get('source')} → {ex.get('target')}**. {ex.get('explanation','')}",'']
    guide += [heading('Viewpoint-guide'),'']
    for x in g.get('viewpoints',[]):
        vv=vp.get(x.get('viewpoint'),{}); guide += [heading(f"{vv.get('name',x.get('viewpoint'))}",3),'','**Använd när**','',bullets(x.get('use_when',[])),'','**Arbetsgång**','', '\n'.join(f"{i+1}. {v}" for i,v in enumerate(x.get('steps',[]))) or '1. -','', '**Frågor vyn hjälper till att besvara**','',bullets(x.get('questions_answered',[])),'']
    guide += [heading('Modelleringsmönster'),'']
    for x in g.get('patterns',[]): guide += [heading(x.get('name'),3),'',x.get('description',''),'',bullets(x.get('when_to_use',[])),'']
    guide += [heading('Antimönster'),'']
    for x in g.get('anti_patterns',[]): guide += [heading(x.get('name'),3),'',x.get('description',''),'']
    guide += [heading('Vanliga frågor'),'']
    for x in g.get('faq',[]): guide += [heading(x.get('question'),3),'',x.get('answer',''),'']

    # quick reference
    q=[f"# {meta['name']} – snabbguide",'',heading('Vilket objekt ska jag använda?'),'',md_table(['När du vill beskriva','Använd','Tänk på'],[[x.get('purpose',''),elem.get(x.get('type'),{}).get('name',x.get('type')), (x.get('do_not_use_when') or [''])[0]] for x in g.get('elements',[])]),'',heading('Relationer'),'',md_table(['Relation','Betydelse','Källa → mål'],[[rel.get(x.get('type'),{}).get('name',x.get('type')),x.get('meaning',''),f"{', '.join(rel.get(x.get('type'),{}).get('source',{}).get('types',[]))} → {', '.join(rel.get(x.get('type'),{}).get('target',{}).get('types',[]))}"] for x in g.get('relationships',[])]),'',heading('Viewpoints'),'',md_table(['Viewpoint','Använd när'],[[vp.get(x.get('viewpoint'),{}).get('name',x.get('viewpoint')),x.get('use_when',[])] for x in g.get('viewpoints',[])]),'']
    return {'reference':'\n'.join(r).rstrip()+'\n','modeling-guide':'\n'.join(guide).rstrip()+'\n','quick-reference':'\n'.join(q).rstrip()+'\n'}

def md_to_confluence(text:str)->str:
    out=[]; in_table=False
    lines=text.splitlines()
    for line in lines:
        if line.startswith('# '): out.append('h1. '+line[2:]); in_table=False
        elif line.startswith('## '): out.append('h2. '+line[3:]); in_table=False
        elif line.startswith('### '): out.append('h3. '+line[4:]); in_table=False
        elif re.match(r'^\|.*\|$',line):
            cells=[c.strip() for c in line.strip('|').split('|')]
            if all(set(c)<=set('-: ') for c in cells): continue
            if not in_table: out.append('||'+'||'.join(cells)+'||'); in_table=True
            else: out.append('|'+'|'.join(cells)+'|')
        elif line.startswith('- '): out.append('* '+line[2:]); in_table=False
        elif re.match(r'^\d+\. ',line): out.append('# '+re.sub(r'^\d+\. ','',line)); in_table=False
        else:
            in_table=False
            line=re.sub(r'\*\*(.+?)\*\*',r'*\1*',line)
            line=re.sub(r'`([^`]+)`',r'{{\1}}',line)
            out.append(line)
    return '\n'.join(out).rstrip()+'\n'

def write_pdf(markdown:str,target:Path,title:str):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, ListFlowable, ListItem
    except ImportError as exc:
        raise RuntimeError('PDF export requires reportlab (pip install reportlab)') from exc
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontSize=8.5,leading=11)); styles['Title'].alignment=TA_CENTER
    doc=SimpleDocTemplate(str(target),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm,title=title)
    story=[]; lines=markdown.splitlines(); i=0
    def fmt(x):
        x=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',x); x=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',x); return x.replace('&','&amp;').replace('&amp;lt;','&lt;').replace('&amp;gt;','&gt;')
    while i<len(lines):
        line=lines[i]
        if line.startswith('# '): story.append(Paragraph(fmt(line[2:]),styles['Title'])); story.append(Spacer(1,8)); i+=1; continue
        if line.startswith('## '): story.append(Spacer(1,6)); story.append(Paragraph(fmt(line[3:]),styles['Heading2'])); i+=1; continue
        if line.startswith('### '): story.append(Paragraph(fmt(line[4:]),styles['Heading3'])); i+=1; continue
        if line.startswith('| '):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                cells=[c.strip().replace('\\|','|') for c in lines[i].strip('|').split('|')]
                if not all(set(c)<=set('-: ') for c in cells): rows.append([Paragraph(fmt(c),styles['Small']) for c in cells])
                i+=1
            if rows:
                t=Table(rows,repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,None),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)])); story.append(t); story.append(Spacer(1,6))
            continue
        if line.startswith('- '):
            items=[]
            while i<len(lines) and lines[i].startswith('- '): items.append(ListItem(Paragraph(fmt(lines[i][2:]),styles['BodyText']))); i+=1
            story.append(ListFlowable(items,bulletType='bullet')); story.append(Spacer(1,4)); continue
        if re.match(r'^\d+\. ',line):
            items=[]
            while i<len(lines) and re.match(r'^\d+\. ',lines[i]): items.append(ListItem(Paragraph(fmt(re.sub(r'^\d+\. ','',lines[i])),styles['BodyText']))); i+=1
            story.append(ListFlowable(items,bulletType='1')); story.append(Spacer(1,4)); continue
        if line.strip(): story.append(Paragraph(fmt(line),styles['BodyText'])); story.append(Spacer(1,4))
        else: story.append(Spacer(1,3))
        i+=1
    doc.build(story)

def main():
    ap=argparse.ArgumentParser(description='Export metamodel reference, modeling guide and quick reference')
    ap.add_argument('model_dir',type=Path); ap.add_argument('output_dir',type=Path)
    ap.add_argument('--document',choices=['reference','modeling-guide','quick-reference','all'],default='all')
    ap.add_argument('--format',choices=['markdown','confluence','pdf','all'],default='all')
    a=ap.parse_args(); docs=model_docs(a.model_dir); a.output_dir.mkdir(parents=True,exist_ok=True)
    kinds=list(docs) if a.document=='all' else [a.document]; fmts=['markdown','confluence','pdf'] if a.format=='all' else [a.format]
    written=[]
    for kind in kinds:
        md=docs[kind]
        for fmt in fmts:
            ext={'markdown':'md','confluence':'confluence','pdf':'pdf'}[fmt]; out=a.output_dir/f'{kind}.{ext}'
            if fmt=='markdown': out.write_text(md,encoding='utf-8')
            elif fmt=='confluence': out.write_text(md_to_confluence(md),encoding='utf-8')
            else: write_pdf(md,out,kind.replace('-',' ').title())
            written.append(str(out))
    print('\n'.join(written))
if __name__=='__main__': main()
