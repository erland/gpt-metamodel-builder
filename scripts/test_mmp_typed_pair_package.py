#!/usr/bin/env python3
"""CORE-016 MMP candidate typed pair profile: transport, roundtrip, legacy safety."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*args):return subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,text=True)
def main():
 with tempfile.TemporaryDirectory() as td:
  work=Path(td);model=work/"model";shutil.copytree(ROOT/"examples/architecture-lite",model)
  file=model/"metamodel.yaml";data=yaml.safe_load(file.read_text())
  data["metamodel"]["namespace"]="https://example.org/core016/typed-pairs"
  data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-typed-pairs","version":"1.0.0"}]
  data["junctions"]=[{"id":"core016_junction","name":"AND"}]
  rel=data["relationships"][0]
  rel["source"]["typed_refs"]=[{"kind":"element","id":v} for v in rel["source"]["types"]]+[{"kind":"junction","id":"core016_junction"}]
  rel["target"]["typed_refs"]=[{"kind":"element","id":v} for v in rel["target"]["types"]]+[{"kind":"relationship","id":rel["id"]}]
  rel["allowed_typed_pairs"]=[{"source":{"kind":"junction","id":"core016_junction"},"target":{"kind":"relationship","id":rel["id"]}}]
  file.write_text(yaml.safe_dump(data,sort_keys=False));original=file.read_bytes()
  package=work/"candidate.zip"
  old=run(sys.executable,ROOT/"scripts/export_mmp.py","--legacy-1-0","--model-dir",model,"--output",work/"old.zip")
  assert old.returncode!=0 and not (work/"old.zip").exists(),old.stderr
  new=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",package)
  assert new.returncode==0,new.stderr
  ok=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
  assert ok.returncode==0,ok.stderr
  sys.path.insert(0,str(ROOT/"interop"))
  from mmp_v1_consumer import consume
  assert consume(package)["package_format_version"]=="1.1.0"
  if "--typescript" in sys.argv:
   ts=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
   assert ts.returncode==0,ts.stderr
   assert json.loads(ts.stdout)["package_format_version"]=="1.1.0"
  dest=work/"imported"
  imported=run(sys.executable,ROOT/"scripts/import_mmp.py","import",package,"--output",dest)
  assert imported.returncode==0,imported.stderr
  assert (dest/"metamodel.yaml").read_bytes()==original
  assert file.read_bytes()==original
  data["metamodel"]["extensions"]["mmp_required_capabilities"].pop()
  file.write_text(yaml.safe_dump(data,sort_keys=False))
  rejected=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",work/"missing.zip")
  assert rejected.returncode!=0 and "mmp-typed-pairs" in rejected.stderr,rejected.stderr
 print("CORE-016 typed pair candidate package PASS")
if __name__=="__main__":main()
