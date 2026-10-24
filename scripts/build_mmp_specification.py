#!/usr/bin/env python3
"""Build a tool-neutral MMP v1 specification and conformance kit."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
FORMAT_VERSION="1.0.0"
SCHEMAS=("mmp-manifest-v1","metamodel","properties","constraints","viewpoints","notation","provenance","version","guidance","common-definitions")
ZIP_DATE=(1980,1,1,0,0,0)

def package(output:Path):
    with tempfile.TemporaryDirectory() as work:
        tmp=Path(work); model=tmp/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        mm=model/"metamodel.yaml"
        data=yaml.safe_load(mm.read_text(encoding="utf-8"))
        data["metamodel"]["namespace"]="https://example.org/mmp/architecture-lite"
        mm.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding="utf-8")
        example=tmp/"architecture-example.mmp.zip"
        cmd=[sys.executable,str(ROOT/"scripts/export_mmp.py"),"--model-dir",str(model),"--output",str(example),"--producer-version","mmp-kit"]
        env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"}
        subprocess.run(cmd,check=True,capture_output=True,env=env)
        entries={
            "README.md":(ROOT/"mmp-kit/README.md").read_bytes(),
            "specification/mmp-v1.md":(ROOT/"docs/mmp-v1-contract.md").read_bytes(),
            "specification/implementation-guide.md":(ROOT/"mmp-kit/implementation-guide.md").read_bytes(),
            "specification/conformance.md":(ROOT/"mmp-kit/conformance.md").read_bytes(),
            "reference-implementation/mmp_v1_consumer.py":(ROOT/"interop/mmp_v1_consumer.py").read_bytes(),
            "examples/architecture-example.mmp.zip":example.read_bytes(),
        }
        for name in SCHEMAS:
            filename=name+".schema.json"
            entries["schemas/"+filename]=(ROOT/"schemas"/filename).read_bytes()
        checksums="".join(f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name,content in sorted(entries.items()))
        entries["SHA256SUMS.txt"]=checksums.encode()
        output.parent.mkdir(parents=True,exist_ok=True)
        if output.exists(): raise FileExistsError(output)
        with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for name,content in sorted(entries.items()):
                info=zipfile.ZipInfo(name,ZIP_DATE)
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,content)
        return output

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);args=ap.parse_args()
    print(package(args.output))
if __name__=="__main__":main()
