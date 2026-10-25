#!/usr/bin/env python3
"""Combined mandatory profile acceptance for one actual MMP 1.1 candidate ZIP."""
import json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*a):return subprocess.run([str(x) for x in a],cwd=ROOT,capture_output=True,text=True)
def verify(package,typescript=False):
 from mmp_v1_consumer import consume
 checks=[run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)]
 errors=[]
 try:consume(package)
 except Exception as exc:errors.append(str(exc))
 if typescript:checks.append(run("node",ROOT/"interop/typescript/dist/consumer.js",package))
 return all(p.returncode==0 for p in checks) and not errors,errors+[p.stderr[-1200:] for p in checks if p.returncode]
def mutate_package(original,dest,change):
 # Keep payload checksums as-is: a changed payload must be detected, never trusted.
 with zipfile.ZipFile(original) as inp,zipfile.ZipFile(dest,"w") as out:
  for entry in inp.infolist():
   data=inp.read(entry.filename)
   if entry.filename=="documentation/required-default-presence.json" and change=="tamper_policy":
    obj=json.loads(data);obj["default_satisfies_required"]=True;data=json.dumps(obj).encode()
   out.writestr(entry,data)
def main():
 with tempfile.TemporaryDirectory() as td:
  w=Path(td);m=w/"model";shutil.copytree(ROOT/"examples/architecture-lite",m)
  file=m/"metamodel.yaml";d=yaml.safe_load(file.read_text())
  d["metamodel"]["namespace"]="https://example.org/internal-combined-profile"
  capabilities=[
   {"id":"mmp-typed-endpoints","version":"1.0.0"},
   {"id":"mmp-typed-pairs","version":"1.0.0"},
   {"id":"mmp-junction-structure","version":"0.1.0"},
   {"id":"mmp-required-default-presence","version":"0.1.0"}]
  d["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=capabilities
  d["junctions"]=[{"id":"gate","name":"Gate"}]
  rel=d["relationships"][0]
  rel["source"]["typed_refs"]=[{"kind":"element","id":x} for x in rel["source"]["types"]]
  rel["target"]["typed_refs"]=[{"kind":"element","id":x} for x in rel["target"]["types"]]+[{"kind":"junction","id":"gate"}]
  rel["allowed_typed_pairs"]=[{"source":rel["source"]["typed_refs"][0],
                               "target":{"kind":"junction","id":"gate"}}]
  file.write_text(yaml.safe_dump(d,sort_keys=False));before=file.read_bytes()
  (m/"profiles").mkdir()
  (m/"profiles"/"junction-structure.json").write_text(json.dumps({
    "profile":"mmp-junction-structure@0.1.0","junction_operators":{"gate":"and"}}))
  (m/"profiles"/"required-default-presence.json").write_text(json.dumps({
    "profile":"mmp-required-default-presence@0.1.0",
    "default_satisfies_required":False,"null_counts_as_present":False}))
  package=w/"good.zip"
  cmd=[sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1",
       "--model-dir",m,"--output",package]
  p=run(*cmd);assert p.returncode==0,p.stderr[-3500:]
  sys.path.insert(0,str(ROOT/"interop"))
  ok,errors=verify(package,"--typescript" in sys.argv);assert ok,errors
  with zipfile.ZipFile(package) as z:
   manifest=yaml.safe_load(z.read("manifest.yaml"))
   assert manifest["required_capabilities"]==capabilities
   assert set(("documentation/junction-structure.json",
      "documentation/required-default-presence.json")).issubset(z.namelist())
  out=w/"restored"
  p=run(sys.executable,ROOT/"scripts/import_mmp.py","import",package,"--output",out)
  assert p.returncode==0,p.stderr[-3500:]
  assert (out/"metamodel.yaml").read_bytes()==before
  tampered=w/"tampered.zip";mutate_package(package,tampered,"tamper_policy")
  ok,_=verify(tampered,"--typescript" in sys.argv);assert not ok,"tampered checksum accepted"
  # Change the canonical mandatory capability without regenerating package checksums.
  # Both consumers must reject a modified declaration.
  with zipfile.ZipFile(package) as inp,zipfile.ZipFile(w/"unknown.zip","w") as outzip:
   for info in inp.infolist():
    payload=inp.read(info.filename)
    if info.filename=="canonical/metamodel.yaml":
     doc=yaml.safe_load(payload)
     doc["metamodel"]["extensions"]["mmp_required_capabilities"][-1]["version"]="99.0.0"
     payload=yaml.safe_dump(doc,sort_keys=False).encode()
    outzip.writestr(info,payload)
  ok,_=verify(w/"unknown.zip","--typescript" in sys.argv)
  assert not ok,"unknown capability accepted"
  # The exporter must also reject a *valid source tree* with mismatched mandatory profiles.
  d["metamodel"]["extensions"]["mmp_required_capabilities"][-1]["version"]="99.0.0"
  file.write_text(yaml.safe_dump(d,sort_keys=False))
  assert run(*cmd).returncode!=0
  legacy=w/"legacy.zip"
  assert run(sys.executable,ROOT/"scripts/export_mmp.py","--model-dir",m,"--output",legacy).returncode!=0
 print("Combined mandatory candidate-profile package PASS")
if __name__=="__main__":main()
