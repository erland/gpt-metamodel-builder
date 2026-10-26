#!/usr/bin/env python3
"""Internal synthetic fixture: large declarative model, not an external standard."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
SPEC=json.loads((ROOT/"tests/fixtures/generic-large-structure-v1.json").read_text())
def run(*args):
 return subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True)
def build_model(folder):
 shutil.copytree(ROOT/"examples/architecture-lite",folder)
 path=folder/"metamodel.yaml"
 data=yaml.safe_load(path.read_text())
 data["metamodel"]["namespace"]="https://example.org/generic-large-structure"
 required=data["metamodel"].setdefault("extensions",{}).setdefault("mmp_required_capabilities",[])
 required.extend([{"id":"mmp-typed-endpoints","version":"1.0.0"},
                  {"id":"mmp-typed-pairs","version":"1.0.0"}])
 groups={}
 for group in SPEC["groups"]:
  ids=[group["id"]+"_"+str(i+1).zfill(2) for i in range(group["count"])]
  groups[group["id"]]=ids
  data["elements"].extend({"id":ident,"name":ident.replace("_"," ").title(),
                           "kind":group["kind"]} for ident in ids)
 all_ids=[ident for ids in groups.values() for ident in ids]
 data.setdefault("junctions",[]).extend(
  {"id":j,"name":j.replace("_"," ").title()} for j in SPEC["junctions"])
 total=0
 for rule in SPEC["relationship_rules"]:
  sources=all_ids if rule["source"]=="*" else groups[rule["source"]]
  targets=all_ids if rule["target"]=="*" else groups[rule["target"]]
  allowed=[{"source":{"kind":"element","id":source},
            "target":{"kind":"element","id":target}}
           for source in sources for target in targets]
  total+=len(allowed)
  data["relationships"].append({
   "id":rule["id"],"name":rule["id"].replace("_"," ").title(),"kind":"custom",
   "directed":True,
   "source":{"types":sources,"typed_refs":[{"kind":"element","id":x} for x in sources],
             "cardinality":"0..*"},
   "target":{"types":targets,"typed_refs":[{"kind":"element","id":x} for x in targets],
             "cardinality":"0..*"},
   "allowed_typed_pairs":allowed})
 assert len(all_ids)==SPEC["expected_generated_elements"]
 assert total==SPEC["expected_generated_pairs"]
 assert len(SPEC["relationship_rules"])==SPEC["expected_new_relationships"]
 path.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
 return path,all_ids
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);source=work/"model"
  path,ids=build_model(source);before=path.read_bytes()
  package=work/"candidate.zip"
  exported=run(sys.executable,ROOT/"scripts/export_mmp.py",
               "--candidate-1-1","--model-dir",source,"--output",package)
  assert exported.returncode==0,exported.stderr[-5000:]
  valid=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert valid.returncode==0,valid.stderr[-5000:]
  sys.path.insert(0,str(ROOT/"interop"))
  from mmp_v1_consumer import consume
  assert consume(package)["package_format_version"]=="1.1.0"
  if "--typescript" in sys.argv:
   result=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert result.returncode==0,result.stderr[-5000:]
  destination=work/"imported"
  result=run(sys.executable,ROOT/"scripts/import_mmp.py","import",
             package,"--output",destination)
  assert result.returncode==0,result.stderr[-5000:]
  restored=(destination/"metamodel.yaml").read_bytes()
  assert restored==before,"Canonical roundtrip lost information"
  parsed=yaml.safe_load(restored)
  added=[r for r in parsed["relationships"] if r["id"] in
         {x["id"] for x in SPEC["relationship_rules"]}]
  assert sum(len(r["allowed_typed_pairs"]) for r in added)==SPEC["expected_generated_pairs"]
  assert len(added)==SPEC["expected_new_relationships"]
  assert len([e for e in parsed["elements"] if e["id"] in ids])==len(ids)
  assert path.read_bytes()==before
  legacy=work/"legacy.zip"
  old=run(sys.executable,ROOT/"scripts/export_mmp.py","--legacy-1-0",
          "--model-dir",source,"--output",legacy)
  assert old.returncode!=0 and not legacy.exists(),"MMP 1.0 downgrade wrongly permitted"
 print("Generic large structural fixture candidate package PASS")
if __name__=="__main__":main()
