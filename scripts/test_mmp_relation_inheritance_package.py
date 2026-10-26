#!/usr/bin/env python3
"""CORE-015 full MMP candidate test: multiple relationship parents, parity, legacy."""
from pathlib import Path
import json, shutil, subprocess, sys, tempfile
import yaml

ROOT=Path(__file__).resolve().parents[1]
def cmd(*args):
    return subprocess.run(list(map(str,args)),cwd=ROOT,text=True,capture_output=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        work=Path(td);src=work/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",src)
        path=src/"metamodel.yaml"
        data=yaml.safe_load(path.read_text())
        data["metamodel"]["namespace"]="https://example.org/core015/relation-inheritance"
        base=data["relationships"][0]
        source=base["source"]["types"][0]
        target=base["target"]["types"][0]
        data["elements"].extend([
            {"id":"inherit_source","name":"Inherited Source","extends":[source]},
            {"id":"inherit_target","name":"Inherited Target","extends":[target]}])
        base["allowed_type_pairs"]=[{"source":source,"target":target}]
        second={"id":"pair_parent_two","name":"Pair Parent Two",
                "source":{"types":[source,"inherit_source"]},
                "target":{"types":[target]},
                "allowed_type_pairs":[{"source":"inherit_source","target":target}]}
        child={"id":"pair_child","name":"Pair Child","extends":[base["id"],"pair_parent_two"],
               "source":{"types":["inherit_source"]},
               "target":{"types":[target]}}
        data["relationships"].extend([second,child])
        cap={"id":"mmp-pairwise-relationships","version":"1.0.0"}
        data["metamodel"].setdefault("extensions",{})["mmp_required_capabilities"]=[cap]
        path.write_text(yaml.safe_dump(data,sort_keys=False))
        before=path.read_bytes()
        package=work/"pairs.zip"
        result=cmd(sys.executable,ROOT/"scripts/export_mmp.py","--candidate-1-1",
                   "--model-dir",src,"--output",package)
        assert result.returncode==0,result.stderr
        assert cmd(sys.executable,ROOT/"scripts/import_mmp.py","validate",package).returncode==0
        sys.path.insert(0,str(ROOT/"interop"))
        from mmp_v1_consumer import consume
        from mmp_effective_pairs import effective_pairs
        expected=effective_pairs(data,"pair_child")
        assert {(item["source"],item["target"]) for item in expected} == {
            ("inherit_source","inherit_target"),("inherit_source",target)
        }
        actual=consume(package)["effective_pairs"]
        assert actual["pair_child"]==expected,actual["pair_child"]
        if "--typescript" in sys.argv:
            js=ROOT/"interop/typescript/dist/consumer.js"
            assert js.is_file(),"Build TypeScript first"
            ts=cmd("node",js,package)
            assert ts.returncode==0,ts.stderr
            assert json.loads(ts.stdout)["effective_pairs"]==actual
        imported=work/"imported"
        check=cmd(sys.executable,ROOT/"scripts/import_mmp.py","import",package,"--output",imported)
        assert check.returncode==0,check.stderr
        assert (imported/"metamodel.yaml").read_bytes()==before
        # Old-format export remains blocked if semantics would be lost.
        old=cmd(sys.executable,ROOT/"scripts/export_mmp.py","--legacy-1-0","--model-dir",src,"--output",work/"legacy.zip")
        assert old.returncode!=0 and not (work/"legacy.zip").exists()
    print("CORE-015 relation-inheritance package parity PASS")
if __name__=="__main__":main()
