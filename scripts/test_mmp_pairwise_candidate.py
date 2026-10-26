#!/usr/bin/env python3
"""CORE-015: candidate MMP roundtrip, legacy safety and mandatory profile checks."""
import sys,tempfile,shutil,subprocess,zipfile,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def run(name,*args):
    return subprocess.run([sys.executable,str(ROOT/"scripts"/name),*map(str,args)],capture_output=True,text=True,cwd=ROOT)
def main():
    with tempfile.TemporaryDirectory() as td:
        root=Path(td);src=root/"src"
        shutil.copytree(ROOT/"examples/architecture-lite",src)
        file=src/"metamodel.yaml";data=yaml.safe_load(file.read_text())
        data["metamodel"]["namespace"]="https://example.org/core015"
        rel=data["relationships"][0]
        rel["allowed_type_pairs"]=[{"source":rel["source"]["types"][0],"target":rel["target"]["types"][0]}]
        cap={"id":"mmp-pairwise-relationships","version":"1.0.0"}
        data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[cap]
        file.write_text(yaml.safe_dump(data,sort_keys=False))
        original=file.read_bytes()
        p=run("export_mmp.py","--legacy-1-0","--model-dir",src,"--output",root/"legacy.zip")
        assert p.returncode!=0 and not (root/"legacy.zip").exists(),p.stderr
        p=run("export_mmp.py","--candidate-1-1","--model-dir",src,"--output",root/"pairs.zip")
        assert p.returncode==0,p.stderr
        with zipfile.ZipFile(root/"pairs.zip") as z:
            manifest=yaml.safe_load(z.read("manifest.yaml"))
        assert manifest["required_capabilities"]==[cap]
        assert run("import_mmp.py","validate",root/"pairs.zip").returncode==0
        p=run("import_mmp.py","import",root/"pairs.zip","--output",root/"new")
        assert p.returncode==0,p.stderr
        assert (root/"new/metamodel.yaml").read_bytes()==original
        assert file.read_bytes()==original
        sys.path.insert(0,str(ROOT/"interop"))
        from mmp_v1_consumer import consume
        assert consume(root/"pairs.zip")["package_format_version"]=="1.1.0"
        del data["metamodel"]["extensions"]["mmp_required_capabilities"]
        file.write_text(yaml.safe_dump(data,sort_keys=False))
        p=run("export_mmp.py","--candidate-1-1","--model-dir",src,"--output",root/"missing.zip")
        assert p.returncode!=0 and "requires explicit" in p.stderr,p.stderr
        assert not (root/"missing.zip").exists()
    print("CORE-015 candidate roundtrip PASS")
if __name__=="__main__":main()
