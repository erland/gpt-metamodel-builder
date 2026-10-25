#!/usr/bin/env python3
"""MMP 1.1 candidate contract tests; preserve legacy canonical and MMP 1.0 behavior."""
import hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
def run(script,*args):
    return subprocess.run([sys.executable,str(ROOT/"scripts"/script),*map(str,args)],
        cwd=ROOT,capture_output=True,text=True,env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"})

def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td); model=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        mm=model/"metamodel.yaml"; obj=yaml.safe_load(mm.read_text())
        obj["metamodel"]["namespace"]="https://example.org/models/legacy"
        mm.write_text(yaml.safe_dump(obj,sort_keys=False))
        original=mm.read_bytes()
        legacy=base/"legacy.zip"
        a=run("export_mmp.py","--model-dir",model,"--output",legacy)
        assert a.returncode==0,a.stderr
        assert yaml.safe_load(zipfile.ZipFile(legacy).read("manifest.yaml"))["package_format_version"]=="1.0.0"
        assert run("import_mmp.py","validate",legacy).returncode==0
        candidate=base/"candidate.zip"
        b=run("export_mmp.py","--model-dir",model,"--candidate-1-1","--output",candidate)
        assert b.returncode==0,b.stderr
        with zipfile.ZipFile(candidate) as z:
            content={n:z.read(n) for n in z.namelist()}
        manifest=yaml.safe_load(content["manifest.yaml"])
        assert manifest["package_format_version"]=="1.1.0"
        assert manifest["required_capabilities"]==[]
        assert run("import_mmp.py","validate",candidate).returncode==0
        out=base/"imported"
        assert run("import_mmp.py","import",candidate,"--output",out).returncode==0
        assert (out/"metamodel.yaml").read_bytes()==original
        assert mm.read_bytes()==original, "Source YAML mutated"
        assert run("import_mmp.py","import",candidate,"--output",out).returncode!=0
        def repack(name,files):
            path=base/name
            with zipfile.ZipFile(path,"w") as z:
                for k,v in files.items():z.writestr(k,v)
            return path
        modified=dict(content); m=yaml.safe_load(modified["manifest.yaml"])
        m["required_capabilities"]=[{"id":"mmp-pairwise-relationships","version":"1.0.0"}]
        modified["manifest.yaml"]=yaml.safe_dump(m).encode()
        rejected=repack("rejected.zip",modified)
        x=run("import_mmp.py","validate",rejected)
        assert x.returncode!=0 and "mismatch" in x.stderr,x.stderr
        modified2=dict(content)
        modeldoc=yaml.safe_load(modified2["canonical/metamodel.yaml"])
        modeldoc["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=m["required_capabilities"]
        modified2["canonical/metamodel.yaml"]=yaml.safe_dump(modeldoc).encode()
        m2=yaml.safe_load(modified2["manifest.yaml"])
        for f in m2["files"]:
            if f["path"]=="canonical/metamodel.yaml":
                f["sha256"]=hashlib.sha256(modified2["canonical/metamodel.yaml"]).hexdigest()
        modified2["manifest.yaml"]=yaml.safe_dump(m2).encode()
        rejected2=repack("unsupported.zip",modified2)
        y=run("import_mmp.py","validate",rejected2)
        assert y.returncode!=0 and "not_supported" in y.stderr,y.stderr
        from importlib.util import spec_from_file_location,module_from_spec
        import sys as _sys
        _sys.path.insert(0,str(ROOT/"interop"))
        from mmp_v1_consumer import consume
        assert consume(candidate)["package_format_version"]=="1.1.0"
        for bad in [rejected,rejected2]:
            try:consume(bad)
            except ValueError:pass
            else:raise AssertionError("Independent Python consumer accepted unsupported profile")
        # Legacy files are readable without rewrite; old 1.0 remains unaffected.
        assert run("import_mmp.py","validate",legacy).returncode==0
    print("CORE-013 candidate PASS: legacy, opt-in roundtrip, mismatch, fail closed, non-destructive import")

if __name__=="__main__":main()
