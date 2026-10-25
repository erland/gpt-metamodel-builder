#!/usr/bin/env python3
"""Internal synthetic advanced structural candidate-package acceptance."""
import json, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_effective_typed_pairs import effective_typed_pairs
from mmp_typed_instance_graph import validate_typed_graph
from mmp_junction_profile_validation import validate_profile_structure
def run(*a): return subprocess.run([str(x) for x in a],cwd=ROOT,capture_output=True,text=True)
def ref(kind,id):return {"kind":kind,"id":id}
def pair(s,t):return {"source":s,"target":t}
def endpoint(refs):
 return {"types":[r["id"] for r in refs if r["kind"]=="element"],
         "typed_refs":refs,"cardinality":"0..*"}
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);source=work/"model"
  shutil.copytree(ROOT/"examples/architecture-lite",source)
  path=source/"metamodel.yaml";data=yaml.safe_load(path.read_text())
  data["metamodel"]["namespace"]="https://example.org/internal-advanced-structure"
  data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-typed-pairs","version":"1.0.0"},
   {"id":"mmp-junction-structure","version":"0.1.0"}]
  data["elements"].extend([
   {"id":"entity_base","name":"Entity Base","abstract":True},
   {"id":"entity_a","name":"Entity A","extends":["entity_base"]},
   {"id":"entity_b","name":"Entity B","extends":["entity_base"]},
   {"id":"entity_c","name":"Entity C","extends":["entity_a","entity_b"]}])
  data["junctions"]=[{"id":"gate_and","name":"Gate And"},{"id":"gate_or","name":"Gate Or"}]
  a=ref("element","entity_a");b=ref("element","entity_b")
  c=ref("element","entity_c");j=ref("junction","gate_and")
  root_pairs=[pair(a,j),pair(b,j),pair(c,j)]
  data["relationships"].extend([
   {"id":"link_primary","name":"Primary Link","source":endpoint([a,b,c]),
    "target":endpoint([j]),"allowed_typed_pairs":root_pairs},
   {"id":"link_policy","name":"Policy Link","source":endpoint([a,b,c]),
    "target":endpoint([j]),"allowed_typed_pairs":[pair(a,j),pair(c,j)]},
   {"id":"link_effective","name":"Effective Link","extends":["link_primary","link_policy"],
    "source":endpoint([a,b,c]),"target":endpoint([j])},
   {"id":"edge_reference","name":"Edge Reference",
    "source":endpoint([j]),"target":endpoint([ref("relationship","link_effective")]),
    "allowed_typed_pairs":[pair(j,ref("relationship","link_effective"))]},
   {"id":"gate_output","name":"Gate Output",
    "source":endpoint([j]),"target":endpoint([a,b,c]),
    "allowed_typed_pairs":[pair(j,a),pair(j,b),pair(j,c)]}])
  profile={"profile":"mmp-junction-structure@0.1.0",
           "junction_operators":{"gate_and":"and","gate_or":"or"}}
  (source/"profiles").mkdir()
  (source/"profiles/junction-structure.json").write_text(json.dumps(profile))
  path.write_text(yaml.safe_dump(data,sort_keys=False));before=path.read_bytes()
  package=work/"model.zip"
  out=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1",
          "--model-dir",source,"--output",package)
  assert out.returncode==0,out.stderr[-4500:]
  result=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert result.returncode==0,result.stderr[-4500:]
  imported=work/"imported"
  result=run(sys.executable,ROOT/"scripts/import_mmp.py","import",package,"--output",imported)
  assert result.returncode==0,result.stderr[-4500:]
  assert (imported/"metamodel.yaml").read_bytes()==before
  model=yaml.safe_load((imported/"metamodel.yaml").read_text())
  with zipfile.ZipFile(package) as z:
   restored_profile=json.loads(z.read("documentation/junction-structure.json"))
  assert restored_profile==profile
  expected=[pair(a,j),pair(c,j)]
  assert effective_typed_pairs(model,"link_effective")==expected
  # Separate opt-in graph population excludes legacy non-typed relation types.
  selected={"link_primary","link_policy","link_effective","edge_reference","gate_output"}
  subset={**model,"relationships":[r for r in model["relationships"] if r["id"] in selected]}
  graph={"complete":True,
   "instances":[{"id":"node_a","type":"entity_a"},{"id":"node_b","type":"entity_b"},
                {"id":"node_c","type":"entity_c"}],
   "junctions":[{"id":"gate1","type":"gate_and"}],
   "edges":[
    {"id":"e1","relationship":"link_effective","source":ref("element","node_c"),
     "target":ref("junction","gate1")},
    {"id":"e2","relationship":"edge_reference","source":ref("junction","gate1"),
     "target":ref("relationship","e1")},
    {"id":"e3","relationship":"gate_output","source":ref("junction","gate1"),
     "target":ref("element","node_a")}]}
  # Relationship-instance cycles are not supported. This acyclic reference is valid.
  assert validate_typed_graph(subset,graph)==[]
  bad=json.loads(json.dumps(graph))
  bad["edges"][0]["source"]=ref("element","node_b")
  try:validate_typed_graph(subset,bad)
  except ValueError as err:assert "typed pair disallowed" in str(err)
  else:raise AssertionError("Parent intersection not enforced")
  # Structural AND/OR operators are profile metadata only, not activation rules.
  structure={"complete":True,"junctions":graph["junctions"],
    "edges":[{"source":edge["source"],"target":edge["target"]}
             for edge in graph["edges"]]}
  assert validate_profile_structure(model,structure,restored_profile)==[]
  incomplete={**structure,"edges":[edge for edge in structure["edges"]
                                    if edge["source"]!=ref("junction","gate1")]}
  assert validate_profile_structure(model,incomplete,restored_profile)
  if "--typescript" in sys.argv:
   consumer=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert consumer.returncode==0,consumer.stderr[-3500:]
   vectors=work/"vectors.json"
   vectors.write_text(json.dumps({"model":subset,"cases":[
    {"id":"complex-accept","graph":graph,"expected":"accept"},
    {"id":"restricted-parent","graph":bad,"expected":"error"}]}))
   result=run("node",ROOT/"interop/typescript/dist/typed-graph-test.js",vectors)
   assert result.returncode==0,result.stderr[-3500:]
   payload=work/"junction.json"
   payload.write_text(json.dumps({"model":model,"profile":restored_profile,
     "cases":[{"graph":structure,"expected":"accept"},
              {"graph":incomplete,"expected":"reject"}]}))
   result=run("node",ROOT/"interop/typescript/dist/junction-profile-graph-test.js",payload)
   assert result.returncode==0,result.stderr[-3500:]
  assert path.read_bytes()==before
 print("Generic advanced-structure candidate package PASS")
if __name__=="__main__":main()
