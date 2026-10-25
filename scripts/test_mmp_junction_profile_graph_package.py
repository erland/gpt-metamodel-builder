#!/usr/bin/env python3
"""Package-bound CORE-016 structural adapter. Tests actual MMP ZIP and shared graph."""
import json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from mmp_junction_profile_validation import validate_profile_structure
def run(*args):return subprocess.run([str(a) for a in args],cwd=ROOT,text=True,capture_output=True)
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);model_dir=work/"model"
  shutil.copytree(ROOT/"examples/architecture-lite",model_dir)
  file=model_dir/"metamodel.yaml";data=yaml.safe_load(file.read_text())
  data["metamodel"]["namespace"]="https://example.org/core016/graph-profile"
  data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-junction-structure","version":"0.1.0"}]
  data["junctions"]=[{"id":"j_and","name":"AND"},{"id":"j_or","name":"OR"}]
  file.write_text(yaml.safe_dump(data,sort_keys=False));before=file.read_bytes()
  profile={"profile":"mmp-junction-structure@0.1.0",
           "junction_operators":{"j_and":"and","j_or":"or"}}
  (model_dir/"profiles").mkdir()
  (model_dir/"profiles/junction-structure.json").write_text(json.dumps(profile))
  package=work/"package.zip"
  result=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1",
             "--model-dir",model_dir,"--output",package)
  assert result.returncode==0,result.stderr
  assert run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package).returncode==0
  with zipfile.ZipFile(package) as archive:
   packaged_model=yaml.safe_load(archive.read("canonical/metamodel.yaml"))
   packaged_profile=json.loads(archive.read("documentation/junction-structure.json"))
  assert packaged_model["junctions"]==data["junctions"]
  assert packaged_profile==profile
  graph={"complete":True,"junctions":[{"id":"a","type":"j_and"},{"id":"b","type":"j_or"}],
         "edges":[
          {"source":{"kind":"element","id":"one"},"target":{"kind":"junction","id":"a"}},
          {"source":{"kind":"junction","id":"a"},"target":{"kind":"element","id":"two"}},
          {"source":{"kind":"element","id":"one"},"target":{"kind":"junction","id":"b"}},
          {"source":{"kind":"junction","id":"b"},"target":{"kind":"element","id":"two"}}]}
  def check(graph,profile,expected):
   try:
    violations=validate_profile_structure(packaged_model,graph,profile)
    actual="reject" if violations else "accept"
   except ValueError as exc:
    actual="not_supported" if "not_supported" in str(exc) else "error"
   assert actual==expected,(actual,expected)
  check(graph,packaged_profile,"accept")
  missing={**graph,"edges":[edge for edge in graph["edges"] if edge["source"].get("id")!="b"]}
  check(missing,packaged_profile,"reject")
  check({**graph,"complete":False},packaged_profile,"not_supported")
  check(graph,{"profile":profile["profile"],"junction_operators":{"j_and":"and"}},"not_supported")
  check(graph,{"profile":profile["profile"],"junction_operators":{"j_and":"xor","j_or":"or"}},"not_supported")
  assert file.read_bytes()==before
  if "--typescript" in sys.argv:
   payload=work/"vectors.json"
   payload.write_text(json.dumps({"model":packaged_model,"profile":packaged_profile,
     "cases":[{"graph":graph,"expected":"accept"},{"graph":missing,"expected":"reject"},
       {"graph":{**graph,"complete":False},"expected":"not_supported"},
       {"graph":graph,"profile":{"profile":profile["profile"],"junction_operators":{"j_and":"and"}},"expected":"not_supported"}]}))
   ts=run("node",ROOT/"interop/typescript/dist/junction-profile-graph-test.js",payload)
   assert ts.returncode==0,ts.stderr
 print("CORE-016 package-bound junction graph PASS")
if __name__=="__main__":main()
