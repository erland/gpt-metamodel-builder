#!/usr/bin/env python3
"""CORE-016 negotiated junction profile package roundtrip and missing-profile failure."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.run([str(x) for x in args],cwd=ROOT,text=True,capture_output=True)
def main():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);model=root/"model";shutil.copytree(ROOT/"examples/architecture-lite",model)
  file=model/"metamodel.yaml";data=yaml.safe_load(file.read_text())
  data["metamodel"]["namespace"]="https://example.org/junction-profile"
  data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-junction-structure","version":"0.1.0"}]
  data["junctions"]=[{"id":"junction_and","name":"Junction AND"}]
  file.write_text(yaml.safe_dump(data,sort_keys=False))
  (model/"profiles").mkdir()
  profile=model/"profiles/junction-structure.json"
  profile.write_text(json.dumps({"profile":"mmp-junction-structure@0.1.0",
                                 "junction_operators":{"junction_and":"and"}}))
  before=file.read_bytes();original_profile=profile.read_bytes()
  package=root/"candidate.zip"
  cmd=[sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",package]
  x=run(*cmd);assert x.returncode==0,x.stderr
  import zipfile
  with zipfile.ZipFile(package) as z:
   assert z.read("documentation/junction-structure.json")==original_profile
   assert "schemas/mmp-junction-structure-profile.schema.json" in z.namelist()
  imported=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert imported.returncode==0,imported.stderr
  sys.path.insert(0,str(ROOT/"interop"))
  from mmp_v1_consumer import consume
  assert consume(package)["package_format_version"]=="1.1.0"
  if "--typescript" in sys.argv:
   ts=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert ts.returncode==0,ts.stderr
  assert file.read_bytes()==before
  output=root/"legacy.zip"
  rejected=run(sys.executable,ROOT/"scripts/export_mmp.py","--model-dir",model,"--output",output)
  assert rejected.returncode!=0 and not output.exists()
  profile.unlink()
  rejected=run(*cmd)
  assert rejected.returncode!=0 and "junction profile" in rejected.stderr
  profile.write_bytes(original_profile)
  data["metamodel"]["extensions"]["mmp_required_capabilities"].pop()
  file.write_text(yaml.safe_dump(data,sort_keys=False))
  rejected=run(*cmd)
  assert rejected.returncode!=0 and "junction profile" in rejected.stderr
 print("CORE-016 junction negotiated profile package PASS")
if __name__=="__main__":main()
