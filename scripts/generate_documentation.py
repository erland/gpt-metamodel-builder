#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
import yaml

FILES = ["metamodel.yaml","properties.yaml","constraints.yaml","viewpoints.yaml","guidance.yaml","notation.yaml","provenance.yaml","version.yaml"]

def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data

def cell(v: Any) -> str:
    if v is None: return ""
    if isinstance(v, list): return ", ".join(str(x) for x in v)
    return str(v).replace("|", "\\|").replace("\n", " ")

def table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"]
    out += ["| " + " | ".join(cell(x) for x in row) + " |" for row in rows]
    return "\n".join(out)

def generate(model_dir: Path) -> str:
    docs={n:load_yaml(model_dir/n) for n in FILES}
    mm, props, cons, views, guidance, notation, prov, ver = [docs[n] for n in FILES]
    meta=mm["metamodel"]
    lines=[f"# {meta['name']} – metamodell", "", meta.get("description", ""), "", "## Metadata", "",
           table(["Fält","Värde"], [["ID",meta.get("id")],["Version",meta.get("version")],["Namespace",meta.get("namespace")],["Standardspråk",meta.get("default_language")]]), ""]
    lines += ["## Elementtyper", "", table(["ID","Namn","Typ","Beskrivning","Property sets"], [[e.get("id"),e.get("name"),e.get("kind"),e.get("description"),e.get("property_sets",[])] for e in mm.get("elements",[])]), ""]
    lines += ["## Relationstyper", "", table(["ID","Namn","Typ","Riktad","Källa","Mål"], [[r.get("id"),r.get("name"),r.get("kind"),r.get("directed"),r.get("source",{}).get("types",[]),r.get("target",{}).get("types",[])] for r in mm.get("relationships",[])]), ""]
    lines += ["## Egenskaper", ""]
    enums={e["id"]:e for e in props.get("enumerations",[])}
    prows=[]
    for p in props.get("property_definitions",[]):
        typ=p.get("type",{})
        t = typ.get("builtin") or typ.get("data_type") or ("enum:"+typ.get("enumeration") if typ.get("enumeration") else "")
        prows.append([p.get("id"),p.get("name"),t,p.get("cardinality"),p.get("required"),p.get("default","")])
    lines += [table(["ID","Namn","Datatyp","Kardinalitet","Obligatorisk","Default"], prows), ""]
    if enums:
        lines += ["### Enumerations", ""]
        for eid,e in enums.items():
            lines += [f"#### {e.get('name',eid)} (`{eid}`)", "", table(["ID","Namn"], [[v.get("id"),v.get("name")] for v in e.get("values",[])]), ""]
    lines += ["## Constraints", "", table(["ID","Namn","Severity","Gäller","Regel","Meddelande"], [[c.get("id"),c.get("name"),c.get("severity"),c.get("applies_to",{}).get("types",[]),c.get("rule",{}).get("expression"),c.get("message")] for c in cons.get("constraints",[])]), ""]
    lines += ["## Viewpoints", ""]
    for v in views.get("viewpoints",[]):
        lines += [f"### {v.get('name')} (`{v.get('id')}`)", "", v.get("description", ""), "", table(["Fält","Värde"], [["Syfte",v.get("purpose")],["Intressenter",v.get("stakeholders",[])],["Element",v.get("allowed_elements",[])],["Relationer",v.get("allowed_relationships",[])],["Obligatoriska element",v.get("required_elements",[])]]), ""]
    lines += ["## Notation", "", table(["ID","Gäller","Form","Visar namn","Visar stereotype","Visar properties"], [[s.get("id"),f"{s.get('applies_to',{}).get('kind')}:{s.get('applies_to',{}).get('type')}",s.get("shape"),s.get("label",{}).get("show_name"),s.get("label",{}).get("show_stereotype"),s.get("label",{}).get("show_properties",[])] for s in notation.get("styles",[])]), ""]
    lines += ["## Provenance", "", "### Källor", "", table(["ID","Namn","Typ","Notering"], [[s.get("id"),s.get("name"),s.get("kind"),s.get("notes")] for s in prov.get("sources",[])]), "", "### Mappningar", "", table(["Mål","Källa","Referens","Relation","Confidence"], [[f"{m.get('target',{}).get('kind')}:{m.get('target',{}).get('id')}",m.get("source",{}).get("source_id"),m.get("source",{}).get("reference"),m.get("relationship"),m.get("confidence")] for m in prov.get("mappings",[])]), ""]
    v=ver.get("version",{})
    lines += ["## Versionsinformation", "", table(["Fält","Värde"], [["Aktuell version",v.get("current")],["Kompatibilitetsnivå",v.get("compatibility",{}).get("level")],["Kompatibel med",v.get("compatibility",{}).get("compatible_with",[])],["Release notes",v.get("release_notes")]]), "", "### Ändringar", "", table(["Typ","Mål","Beskrivning","Breaking"], [[c.get("type"),c.get("target"),c.get("summary"),c.get("breaking")] for c in v.get("changes",[])]), ""]
    return "\n".join(lines).rstrip()+"\n"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("model_dir", type=Path); ap.add_argument("output", type=Path)
    a=ap.parse_args(); text=generate(a.model_dir); a.output.parent.mkdir(parents=True, exist_ok=True); a.output.write_text(text, encoding="utf-8"); print(a.output)
if __name__=="__main__": main()
