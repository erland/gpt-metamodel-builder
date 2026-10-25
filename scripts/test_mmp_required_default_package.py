#!/usr/bin/env python3
"""Package-bound required/default profile positive and negative acceptance."""
import json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
 return subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True)
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);model=work/"model";shutil.copytree(ROOT/"examples/architecture-lite",model)
  path=model/"metamodel.yaml";data=yaml.safe_load(path.read_text())
  data["metamodel"]["namespace"]="https://example.org/presence-package"
  cap={"id":"mmp-required-default-presence","version":"0.1.0"}
  data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[cap]
  path.write_text(yaml.safe_dump(data,sort_keys=False))
  (model/"profiles").mkdir()
  profile=model/"profiles"/"required-default-presence.json"
  policy={"profile":"mmp-required-default-presence@0.1.0",
          "default_satisfies_required":False,"null_counts_as_present":False}
  profile.write_text(json.dumps(policy))
  package=work/"candidate.zip"
  cmd=[sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1",
       "--model-dir",model,"--output",package]
  result=run(*cmd);assert result.returncode==0,result.stderr[-3000:]
  result=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert result.returncode==0,result.stderr[-3000:]
  sys.path.insert(0,str(ROOT/"interop"))
  from mmp_v1_consumer import consume
  assert consume(package)["package_format_version"]=="1.1.0"
  if "--typescript" in sys.argv:
   result=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert result.returncode==0,result.stderr[-3000:]
  with zipfile.ZipFile(package) as z:
   assert json.loads(z.read("documentation/required-default-presence.json"))==policy
  legacy=work/"legacy.zip"
  assert run(sys.executable,ROOT/"scripts/export_mmp.py","--model-dir",model,"--output",legacy).returncode!=0
  # Absent profile document must not be silently accepted.
  profile.unlink()
  result=run(*cmd);assert result.returncode!=0 and "required/default" in result.stderr
  # Malformed document is rejected before packaging.
  profile.write_text(json.dumps({**policy,"default_satisfies_required":True}))
  result=run(*cmd);assert result.returncode!=0
  profile.write_text(json.dumps(policy))
  data["metamodel"]["extensions"]["mmp_required_capabilities"]=[]
  path.write_text(yaml.safe_dump(data,sort_keys=False))
  result=run(*cmd);assert result.returncode!=0 and "required/default" in result.stderr
  # Unknown mandatory version must also fail closed.
  data["metamodel"]["extensions"]["mmp_required_capabilities"]=[{**cap,"version":"99.0.0"}]
  path.write_text(yaml.safe_dump(data,sort_keys=False))
  result=run(*cmd);assert result.returncode!=0
 print("Required/default candidate package negotiation PASS")
if __name__=="__main__":main()
