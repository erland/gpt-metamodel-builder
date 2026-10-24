#!/usr/bin/env python3
"""Functional MMP roundtrip, tamper resistance and safe import regression tests."""
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

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "scripts/export_mmp.py"
IMPORT = ROOT / "scripts/import_mmp.py"

def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          cwd=ROOT, text=True, capture_output=True,
                          env={**os.environ, "SOURCE_DATE_EPOCH":"1792843200"})

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td)
        model=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        mm=model/"metamodel.yaml"
        obj=yaml.safe_load(mm.read_text())
        obj["metamodel"]["namespace"]="https://example.org/metamodels/architecture-lite"
        mm.write_text(yaml.safe_dump(obj,sort_keys=False,allow_unicode=True))
        pkg=base/"source.mmp.zip"
        p=run(EXPORT,"--model-dir",model,"--output",pkg)
        assert p.returncode==0,p.stderr
        for mode in ("inspect","validate"):
            p=run(IMPORT,mode,pkg)
            assert p.returncode==0,p.stderr
            assert json.loads(p.stdout)["verified_sha256_files"]>=15
        out=base/"imported"
        p=run(IMPORT,"import",pkg,"--output",out)
        assert p.returncode==0,p.stderr
        for name in ("metamodel.yaml","properties.yaml","version.yaml","guidance.yaml"):
            assert (out/name).read_bytes()==(model/name).read_bytes()
        p=run(IMPORT,"import",pkg,"--output",out)
        assert p.returncode!=0 and "overwrite" in p.stderr
        with zipfile.ZipFile(pkg) as z:
            contents={name:z.read(name) for name in z.namelist()}
        def repack(name, data):
            dest=base/name
            with zipfile.ZipFile(dest,"w") as z:
                for key,value in data.items():
                    z.writestr(key,value)
            return dest
        tampered=dict(contents)
        tampered["canonical/metamodel.yaml"]+=b"\n# tampered\n"
        assert run(IMPORT,"validate",repack("tampered.zip",tampered)).returncode!=0
        unsafe=dict(contents)
        unsafe["../traversal.txt"]=b"bad"
        assert run(IMPORT,"inspect",repack("unsafe.zip",unsafe)).returncode!=0
        missing=dict(contents)
        del missing["schemas/common-definitions.schema.json"]
        assert run(IMPORT,"validate",repack("missing.zip",missing)).returncode!=0
        duplicate=base/"duplicate.zip"
        with zipfile.ZipFile(duplicate,"w") as z:
            for key,value in contents.items():
                z.writestr(key,value)
            z.writestr("manifest.yaml",contents["manifest.yaml"])
        assert run(IMPORT,"inspect",duplicate).returncode!=0
        changed=dict(contents)
        manifest=yaml.safe_load(changed["manifest.yaml"])
        manifest["package_format_version"]="2.0.0"
        changed["manifest.yaml"]=yaml.safe_dump(manifest).encode()
        assert run(IMPORT,"inspect",repack("version.zip",changed)).returncode!=0
    print("MMP import PASS: inspect, validate, roundtrip, overwrite, tamper, traversal, missing schema, duplicate, version")


if __name__=="__main__":
    main()
