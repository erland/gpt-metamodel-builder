#!/usr/bin/env python3
"""End-to-end independent MMP consumer compatibility test."""
import importlib.util
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

def cmd(*args):
    return subprocess.run([sys.executable,*map(str,args)],cwd=ROOT,
                          text=True,capture_output=True,env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"})

def main():
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)
        source=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",source)
        mm=source/"metamodel.yaml"
        data=yaml.safe_load(mm.read_text())
        data["metamodel"]["namespace"]="https://example.org/metamodels/architecture-lite"
        mm.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True))
        pkg=base/"model.mmp.zip"
        p=cmd(EXPORT,"--model-dir",source,"--output",pkg,"--producer-version","test")
        assert p.returncode==0,p.stderr
        p=cmd(CONSUMER,pkg)
        assert p.returncode==0,p.stderr
        out=json.loads(p.stdout)
        assert {x["id"] for x in out["elements"]}=={x["id"] for x in data["elements"]}
        assert {x["id"] for x in out["relationships"]}=={x["id"] for x in data["relationships"]}
        assert out["properties"] and out["enumerations"] and out["property_sets"]
        # Directory variant can be read without exporter-specific import APIs.
        directory=base/"directory"
        p=cmd(EXPORT,"--model-dir",source,"--output",directory,"--directory")
        assert p.returncode==0,p.stderr
        assert cmd(CONSUMER,directory).returncode==0
        with zipfile.ZipFile(pkg) as z:
            original={name:z.read(name) for name in z.namelist()}
        original["canonical/metamodel.yaml"]+=b"\n# modified\n"
        tampered=base/"tampered.zip"
        with zipfile.ZipFile(tampered,"w") as z:
            for k,v in original.items(): z.writestr(k,v)
        assert cmd(CONSUMER,tampered).returncode!=0
        print("MMP independent consumer PASS: exported ZIP+dir, types/relationships/properties, rejected tampering")

if __name__=="__main__": main()
