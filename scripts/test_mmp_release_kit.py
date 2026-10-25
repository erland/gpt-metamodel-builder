#!/usr/bin/env python3
"""Verify reproducible MMP Specification Kit, inventory hashes and release scope."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILDER=ROOT/"scripts/build_mmp_specification.py"
REQUIRED={
 "README.md","SHA256SUMS.txt","specification/mmp-v1.md","specification-kit.json",
 "specification/version-compatibility-decision.md",
 "conformance/mmp-version-decision-v1.json",
 "conformance/strict-core-coverage-v1.json",
 "conformance/test-manifest.json",
 "conformance/package-semantic-manifest.json",
 "examples/architecture-example.mmp.zip",
 "reference-implementation/mmp_v1_consumer.py"
}

def sha(raw): return hashlib.sha256(raw).hexdigest()

def verify(kit:Path):
    with zipfile.ZipFile(kit) as archive:
        names=archive.namelist()
        assert len(names)==len(set(names)), "Duplicate archive entries"
        assert REQUIRED<=set(names),f"Missing: {REQUIRED-set(names)}"
        text=archive.read("SHA256SUMS.txt").decode("utf-8")
        observed={}
        for line in text.splitlines():
            digest,path=line.split("  ",1)
            assert path not in observed and len(digest)==64
            observed[path]=digest
        assert set(observed)==set(names)-{"SHA256SUMS.txt"},"Checksum inventory differs"
        for path,digest in observed.items():
            assert sha(archive.read(path))==digest, f"Hash mismatch {path}"
        kit_meta=json.loads(archive.read("specification-kit.json"))
        assert kit_meta["specification_kit_version"]=="1.1.0"
        assert kit_meta["package_format_version"]=="1.0.0"
        assert kit_meta["package_format"]=="mmp"
        decision=json.loads(archive.read("conformance/mmp-version-decision-v1.json"))
        assert decision["stable_format"]=="1.0.0"
        assert decision["full_core_1_1"]=="not_verified"
        assert decision["next_format_version"]=="deferred"
        baseline=json.loads(archive.read("conformance/test-manifest.json"))
        extra=json.loads(archive.read("conformance/package-semantic-manifest.json"))
        assert len(baseline["cases"])==9
        assert len(extra["cases"])>=6
        for case in [*baseline["cases"],*extra["cases"]]:
            assert sha(archive.read(case["package"]))==case["sha256"],case["id"]
        return {"files":len(names),"baseline_packages":len(baseline["cases"]),
                "additional_packages":len(extra["cases"]),"sha256":sha(kit.read_bytes())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--kit",type=Path,help="Verify an existing artifact instead of building one")
    ap.add_argument("--json-out",type=Path)
    args=ap.parse_args()
    if args.kit:
        result=verify(args.kit)
    else:
        with tempfile.TemporaryDirectory() as d:
            paths=[Path(d)/"first.zip",Path(d)/"second.zip"]
            for path in paths:
                subprocess.run([sys.executable,str(BUILDER),"--output",str(path)],cwd=ROOT,check=True)
            assert paths[0].read_bytes()==paths[1].read_bytes(),"Build is not bit-reproducible"
            result=verify(paths[0])
    result={"status":"pass","kit_version":"1.1.0","reproducible":not bool(args.kit),
            "mmp_1_1_core":"not_verified",**result}
    print(json.dumps(result,indent=2))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True,exist_ok=True)
        args.json_out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return 0
if __name__=="__main__":raise SystemExit(main())
