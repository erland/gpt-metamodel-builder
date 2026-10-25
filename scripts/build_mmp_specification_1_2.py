#!/usr/bin/env python3
"""Build separate experimental Specification Kit 1.2.0 for MMP 1.1 format."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ZIP_DATE=(1980,1,1,0,0,0)
KIT_VERSION="1.2.0"
def build(output:Path):
 with tempfile.TemporaryDirectory() as td:
  legacy=Path(td)/"legacy.zip"
  subprocess.run([sys.executable,str(ROOT/"scripts/build_mmp_specification.py"),"--output",str(legacy)],check=True,cwd=ROOT)
  with zipfile.ZipFile(legacy) as z:
   entries={name:z.read(name) for name in z.namelist() if name!="SHA256SUMS.txt"}
  meta={"specification_kit_version":KIT_VERSION,"package_format":"mmp","package_format_version":"1.1.0",
        "release_scope":"limited declared capability profiles; no full Core or instance conformance"}
  entries["specification-kit.json"]=(json.dumps(meta,indent=2,sort_keys=True)+"\n").encode()
  entries["specification/mmp-1-1-limited-contract.md"]=(ROOT/"docs/mmp-11-version-scope-freeze.md").read_bytes()
  entries["specification/mmp-1-1-combined-profiles.md"]=(ROOT/"docs/mmp-11-combined-profiles-package-test.md").read_bytes()
  entries["conformance/mmp-1-1-version-scope.json"]=(ROOT/"conformance/mmp-11-version-scope-freeze.json").read_bytes()
  entries["conformance/mmp-1-1-limited-release-decision.json"]=(ROOT/"conformance/mmp-11-limited-release-decision.json").read_bytes()
  entries["schemas/mmp-manifest-1-1-candidate.schema.json"]=(ROOT/"schemas/mmp-manifest-1-1-candidate.schema.json").read_bytes()
  entries["schemas/mmp-junction-structure-profile.schema.json"]=(ROOT/"schemas/mmp-junction-structure-profile.schema.json").read_bytes()
  entries["schemas/mmp-required-default-presence-profile.schema.json"]=(ROOT/"schemas/mmp-required-default-presence-profile.schema.json").read_bytes()
  entries["reference-implementation/mmp_1_1_combined_acceptance.py"]=(ROOT/"scripts/test_mmp_11_combined_profiles_package.py").read_bytes()
  entries["conformance/required-default-presence-v1.json"]=(ROOT/"interop/required-default-presence-v1.json").read_bytes()
  entries["README.md"]+=b"\n\nNOTICE: This 1.2.0 kit includes experimental MMP 1.1 declared-profile contracts. Full Core 1.1 conformance is NOT claimed. Earlier specification documents describe the 1.0 baseline.\n"
  entries["SHA256SUMS.txt"]="".join(f"{hashlib.sha256(v).hexdigest()}  {k}\n" for k,v in sorted(entries.items())).encode()
  if output.exists():raise FileExistsError(output)
  output.parent.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as z:
   for name,content in sorted(entries.items()):
    item=zipfile.ZipInfo(name,ZIP_DATE);item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
    z.writestr(item,content)
 return output
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--output",type=Path,default=Path("mmp-specification-kit-1.2.0.zip"));p.add_argument("--print-filename",action="store_true")
 a=p.parse_args()
 if a.print_filename:print("mmp-specification-kit-1.2.0.zip")
 else:print(build(a.output))
