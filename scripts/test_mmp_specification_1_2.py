#!/usr/bin/env python3
"""Reproducibility and integrity gate for *separate* 1.2.0 candidate kit."""
import hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(x):return hashlib.sha256(x).hexdigest()
def inspect(path):
 with zipfile.ZipFile(path) as z:
  names=z.namelist()
  assert len(names)==len(set(names))
  required={"specification-kit.json","SHA256SUMS.txt","specification/mmp-1-1-limited-contract.md",
   "conformance/mmp-1-1-version-scope.json","schemas/mmp-manifest-1-1-candidate.schema.json",
   "schemas/mmp-required-default-presence-profile.schema.json",
   "specification/release-notes-1.2.0.md","conformance/release-status-1.2.0.json"}
  assert required<=set(names),required-set(names)
  inv={}
  for line in z.read("SHA256SUMS.txt").decode().splitlines():
   digest,name=line.split("  ",1)
   assert name not in inv
   inv[name]=digest
  assert set(inv)==set(names)-{"SHA256SUMS.txt"}
  for name,digest in inv.items():assert sha(z.read(name))==digest,name
  meta=json.loads(z.read("specification-kit.json"))
  assert meta["specification_kit_version"]=="1.2.0"
  assert meta["package_format_version"]=="1.1.0"
  assert "no full Core" in meta["release_scope"], meta["release_scope"]
  readme=z.read("README.md").decode()
  notes=z.read("specification/release-notes-1.2.0.md").decode()
  assert "Specification Kit 1.2.0" in readme and "package format 1.1.0" in readme
  assert "first distributed in project release **v1.4.0**" in readme
  assert "first published with project release **v1.4.0**" in notes
  assert "historical candidate decisions" in readme
  status=json.loads(z.read("conformance/release-status-1.2.0.json"))
  assert status["status"]=="published_limited_scope" and status["first_project_release"]=="v1.4.0"
  historic=json.loads(z.read("conformance/mmp-1-1-limited-release-decision.json"))
  assert historic["decision"]=="conditional_no_go", "do not rewrite historic release decision"
  assert "targets package format 1.0.0" in readme and "Core 1.1 certification" in notes
  old=json.loads(z.read("conformance/mmp-version-decision-v1.json"))
  assert old["stable_format"]=="1.0.0" # archived baseline, not new release status
  return {"files":len(names),"sha256":sha(path.read_bytes())}
def main():
 with tempfile.TemporaryDirectory() as td:
  root=Path(td);a=root/"first.zip";b=root/"second.zip"
  for dest in [a,b]:
   subprocess.run([sys.executable,str(ROOT/"scripts/build_mmp_specification_1_2.py"),"--output",str(dest)],cwd=ROOT,check=True,capture_output=True)
  assert a.read_bytes()==b.read_bytes(),"non-reproducible candidate kit"
  info=inspect(a)
  print(json.dumps({"status":"pass","kit_version":"1.2.0","format_version":"1.1.0",
   "reproducible":True,"release_status":"published_limited_scope",**info},indent=2))
if __name__=="__main__":main()
