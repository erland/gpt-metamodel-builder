#!/usr/bin/env python3
"""Validate the *exact* candidate kit artifact selected for release.

No tag creation, release publication or upload is performed here.
"""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
from test_mmp_specification_1_2 import inspect

ROOT=Path(__file__).resolve().parents[1]
def call(*args):
 subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--kit",type=Path,required=True)
 ap.add_argument("--sha256-file",type=Path,required=True)
 ap.add_argument("--typescript",action="store_true")
 ap.add_argument("--report",type=Path)
 args=ap.parse_args()
 artifact=args.kit.resolve()
 assert artifact.is_file(),artifact
 info=inspect(artifact)
 expected=args.sha256_file.read_text().strip().split()
 assert len(expected)==2 and expected[1] in (artifact.name,str(artifact)), "checksum path mismatch"
 assert expected[0]==info["sha256"],"candidate artifact SHA256 mismatch"
 with tempfile.TemporaryDirectory() as tmp:
  rebuilt=Path(tmp)/artifact.name
  call(sys.executable,ROOT/"scripts/build_mmp_specification_1_2.py","--output",rebuilt)
  assert rebuilt.read_bytes()==artifact.read_bytes(),"artifact differs from source-rebuilt kit"
 # Existing legacy kit verifies the separate v1.0 baseline and its fixture inventory.
 call(sys.executable,ROOT/"scripts/test_mmp_release_kit.py")
 call(sys.executable,ROOT/"scripts/test_mmp_11_candidate_release_gate.py",*(["--typescript"] if args.typescript else []))
 call(sys.executable,ROOT/"scripts/test_mmp_11_combined_profiles_package.py",*(["--typescript"] if args.typescript else []))
 result={"status":"pass","release_decision":"verification_only_no_automatic_go",
         "kit_version":"1.2.0","package_format_version":"1.1.0",
         "sha256":info["sha256"],"file_count":info["files"],
         "source_rebuild_matches":True,"legacy_regression":"pass",
         "candidate_profiles":"pass","combined_profiles":"pass",
         "typescript":args.typescript}
 if args.report:
  args.report.parent.mkdir(parents=True,exist_ok=True)
  args.report.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
