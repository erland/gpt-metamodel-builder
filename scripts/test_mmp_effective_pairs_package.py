#!/usr/bin/env python3
"""Full MMP candidate test comparing Python and TypeScript normalized relations."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def main():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td);model=base/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        f=model/"metamodel.yaml";d=yaml.safe_load(f.read_text())
        d["metamodel"]["namespace"]="https://example.org/normalized-pairs"
        rel=d["relationships"][0]
        source=rel["source"]["types"][0];target=rel["target"]["types"][0]
        d["elements"].extend([
            {"id":"core015_source_child","name":"Source Child","extends":[source]},
            {"id":"core015_target_child","name":"Target Child","extends":[target]}])
        rel["allowed_type_pairs"]=[{"source":source,"target":target}]
        d["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[
            {"id":"mmp-pairwise-relationships","version":"1.0.0"}]
        f.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True))
        pkg=base/"candidate.zip"
        p=subprocess.run([sys.executable,str(ROOT/"scripts/export_mmp.py"),
            "--candidate-1-1","--model-dir",str(model),"--output",str(pkg)],
            cwd=ROOT,text=True,capture_output=True)
        assert p.returncode==0,p.stderr
        sys.path.insert(0,str(ROOT/"interop"))
        from mmp_v1_consumer import consume
        actual=consume(pkg)["effective_pairs"][rel["id"]]
        assert {"source":"core015_source_child","target":"core015_target_child"} in actual,actual
        assert actual==sorted(actual,key=lambda v:(v["source"],v["target"])),actual
        if "--typescript" in sys.argv:
            js=ROOT/"interop/typescript/dist/consumer.js"
            assert js.exists(),"Build TypeScript before cross-language test"
            p=subprocess.run(["node",str(js),str(pkg)],cwd=ROOT,capture_output=True,text=True)
            assert p.returncode==0,p.stderr
            other=json.loads(p.stdout)["effective_pairs"][rel["id"]]
            assert other==actual,{"python":actual,"typescript":other}
        # A legacy model must never gain implied exact pairs.
        del rel["allowed_type_pairs"]
        del d["metamodel"]["extensions"]["mmp_required_capabilities"]
        f.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True))
        old=base/"legacy.zip"
        q=subprocess.run([sys.executable,str(ROOT/"scripts/export_mmp.py"),
            "--model-dir",str(model),"--output",str(old)],cwd=ROOT,text=True,capture_output=True)
        assert q.returncode==0,q.stderr
        assert consume(old)["effective_pairs"]=={}
    print("CORE-015 cross-language effective pairs PASS")
if __name__=="__main__":main()
