#!/usr/bin/env python3
"""Independent consumer must reject semantic corruption even when rehashed."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,text=True,capture_output=True,
                          env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"})
def alter(original, path, action, output):
    with zipfile.ZipFile(original) as z:
        blobs={p:z.read(p) for p in z.namelist()}
    doc=yaml.safe_load(blobs[path]); action(doc)
    blobs[path]=yaml.safe_dump(doc,sort_keys=False,allow_unicode=True).encode()
    manifest=yaml.safe_load(blobs["manifest.yaml"])
    for entry in manifest["files"]:
        entry["sha256"]=hashlib.sha256(blobs[entry["path"]]).hexdigest()
    blobs["manifest.yaml"]=yaml.safe_dump(manifest,sort_keys=False,allow_unicode=True).encode()
    with zipfile.ZipFile(output,"w") as z:
        for key,value in blobs.items(): z.writestr(key,value)

def main():
    with tempfile.TemporaryDirectory() as td:
        temp=Path(td)
        source=temp/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",source)
        path=source/"metamodel.yaml"; doc=yaml.safe_load(path.read_text())
        doc["metamodel"]["namespace"]="https://example.org/architecture-lite"
        path.write_text(yaml.safe_dump(doc,sort_keys=False,allow_unicode=True))
        pkg=temp/"valid.mmp.zip"
        p=run("scripts/export_mmp.py","--model-dir",source,"--output",pkg)
        assert p.returncode==0,p.stderr
        assert run("interop/mmp_v1_consumer.py",pkg).returncode==0
        cases=[
            ("duplicate", "canonical/metamodel.yaml",lambda d:d["elements"].append(dict(d["elements"][0]))),
            ("cycle", "canonical/metamodel.yaml",lambda d:d["elements"][0].update(extends=[d["elements"][0]["id"]])),
            ("unknown-set", "canonical/metamodel.yaml",lambda d:d["elements"][0].update(property_sets=["unknown"])),
            ("unknown-property", "canonical/properties.yaml",lambda d:d["property_sets"][0].update(properties=["unknown"])),
            ("unknown-enum", "canonical/properties.yaml",lambda d:d["property_definitions"][0].update(type={"enumeration":"unknown"})),
        ]
        for name,key,mutation in cases:
            dest=temp/(name+".mmp.zip")
            alter(pkg,key,mutation,dest)
            p=run("interop/mmp_v1_consumer.py",dest)
            assert p.returncode!=0, f"{name} unexpectedly accepted: {p.stdout}"
        print("Independent semantic checks PASS: 5 mutated packages rejected")

if __name__=="__main__": main()
