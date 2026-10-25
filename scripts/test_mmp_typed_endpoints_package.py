#!/usr/bin/env python3
"""CORE-016 opt-in typed endpoint MMP package roundtrip and cross-language parity."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def run(*args):
    return subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,text=True)
def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); model=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        f=model/"metamodel.yaml"; data=yaml.safe_load(f.read_text())
        data["metamodel"]["namespace"]="https://example.org/core016/typed"
        data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[{"id":"mmp-typed-endpoints","version":"1.0.0"}]
        data["junctions"]=[{"id":"core016_junction","name":"AND junction"}]
        rel=data["relationships"][0]
        rel["source"]["typed_refs"]=[{"kind":"element","id":x} for x in rel["source"]["types"]]+[{"kind":"junction","id":"core016_junction"}]
        rel["target"]["typed_refs"]=[{"kind":"element","id":x} for x in rel["target"]["types"]]+[{"kind":"relationship","id":rel["id"]}]
        f.write_text(yaml.safe_dump(data,sort_keys=False))
        original=f.read_bytes()
        output=base/"typed.zip"
        fail=run(sys.executable,ROOT/"scripts/export_mmp.py","--model-dir",model,"--output",base/"legacy.zip")
        assert fail.returncode!=0 and "CORE-016" in fail.stderr,fail.stderr
        assert not (base/"legacy.zip").exists()
        p=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",output)
        assert p.returncode==0,p.stderr
        q=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",output)
        assert q.returncode==0,q.stderr
        sys.path.insert(0,str(ROOT/"interop"))
        from mmp_v1_consumer import consume
        assert consume(output)["package_format_version"]=="1.1.0"
        if "--typescript" in sys.argv:
            ts=run("node",ROOT/"interop/typescript/dist/consumer.js",output)
            assert ts.returncode==0,ts.stderr
            assert json.loads(ts.stdout)["package_format_version"]=="1.1.0"
        dest=base/"imported"
        i=run(sys.executable,ROOT/"scripts/import_mmp.py","import",output,"--output",dest)
        assert i.returncode==0,i.stderr
        assert (dest/"metamodel.yaml").read_bytes()==original
        assert f.read_bytes()==original
        del data["metamodel"]["extensions"]["mmp_required_capabilities"]
        f.write_text(yaml.safe_dump(data,sort_keys=False))
        n=run(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1","--model-dir",model,"--output",base/"missing.zip")
        assert n.returncode!=0 and "CORE-016" in n.stderr,n.stderr
    print("CORE-016 MMP candidate package PASS")
if __name__=="__main__":main()
