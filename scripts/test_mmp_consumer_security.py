#!/usr/bin/env python3
"""Security regression checks for the stand-alone MMP reference consumer."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]
CONSUMER=ROOT/"interop/mmp_v1_consumer.py"
EXPORT=ROOT/"scripts/export_mmp.py"

def run(script,*args):
    return subprocess.run([sys.executable,str(script),*map(str,args)],cwd=ROOT,
                          capture_output=True,text=True,env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"})

def zip_files(path, files):
    with zipfile.ZipFile(path,"w") as z:
        for key,payload in files.items():
            z.writestr(key,payload)

def manifest_change(files, modifier):
    files=dict(files)
    m=yaml.safe_load(files["manifest.yaml"])
    modifier(files,m)
    for item in m["files"]:
        if item["path"] in files:
            item["sha256"]=hashlib.sha256(files[item["path"]]).hexdigest()
    files["manifest.yaml"]=yaml.safe_dump(m,sort_keys=False).encode()
    return files

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)
        model=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        mm=model/"metamodel.yaml"
        data=yaml.safe_load(mm.read_text())
        data["metamodel"]["namespace"]="https://example.org/metamodels/architecture-lite"
        mm.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
        original=base/"original.mmp.zip"
        p=run(EXPORT,"--model-dir",model,"--output",original)
        assert p.returncode==0,p.stderr
        with zipfile.ZipFile(original) as z:
            files={key:z.read(key) for key in z.namelist()}
        assert run(CONSUMER,original).returncode==0
        # Missing file with unchanged manifest: rejected deterministically.
        missing=dict(files)
        del missing["canonical/properties.yaml"]
        dest=base/"missing.zip"
        zip_files(dest,missing)
        p=run(CONSUMER,dest)
        assert p.returncode!=0 and "manifest inventory" in p.stderr,p.stderr
        # External schema reference, with corrected file hash, must be rejected
        # without attempting any network resolution.
        def inject_remote(blobs, manifest):
            path="schemas/metamodel.schema.json"
            schema=json.loads(blobs[path])
            schema["$defs"]["elementType"]["properties"]["id"]={"$ref":"https://example.invalid/evil.json"}
            blobs[path]=json.dumps(schema).encode()
        remote=manifest_change(files,inject_remote)
        dest=base/"external-ref.zip"
        zip_files(dest,remote)
        p=run(CONSUMER,dest)
        assert p.returncode!=0 and "Nonlocal" in p.stderr,p.stderr
        # Missing locally referenced schema, also with updated manifest and hashes.
        def inject_missing_ref(blobs, manifest):
            path="schemas/metamodel.schema.json"
            schema=json.loads(blobs[path])
            schema["$defs"]["elementType"]["properties"]["id"]={"$ref":"missing.schema.json#/$defs/id"}
            blobs[path]=json.dumps(schema).encode()
        local=manifest_change(files,inject_missing_ref)
        dest=base/"missing-ref.zip"
        zip_files(dest,local)
        p=run(CONSUMER,dest)
        assert p.returncode!=0 and "unresolved" in p.stderr,p.stderr
        # Path traversal fails regardless of manifest content.
        dest=base/"traversal.zip"
        zip_files(dest,{**files,"../escape.txt":b"no"})
        assert run(CONSUMER,dest).returncode!=0
    print("MMP consumer security PASS: missing files, remote/missing schemas, traversal rejected")

if __name__=="__main__":
    main()
