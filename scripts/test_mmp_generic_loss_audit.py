#!/usr/bin/env python3
"""Verify full candidate-package preservation, report inventory and negative drift."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from test_mmp_generic_large_fixture import build_model, SPEC
from mmp_fixture_loss_audit import compare, inventory

def run(*args):
    return subprocess.run([str(a) for a in args],cwd=ROOT,capture_output=True,text=True)

def main():
    with tempfile.TemporaryDirectory() as td:
        folder=Path(td);source=folder/"model"
        path,generated=build_model(source)
        original=yaml.safe_load(path.read_bytes())
        package=folder/"candidate.zip"
        exported=run(sys.executable,ROOT/"scripts/export_mmp.py",
                     "--candidate-1-1","--model-dir",source,"--output",package)
        assert exported.returncode==0,exported.stderr[-3000:]
        checked=run(sys.executable,ROOT/"scripts/import_mmp.py","validate",package)
        assert checked.returncode==0,checked.stderr[-3000:]
        imported=folder/"imported"
        restored=run(sys.executable,ROOT/"scripts/import_mmp.py","import",
                     package,"--output",imported)
        assert restored.returncode==0,restored.stderr[-3000:]
        recovered=yaml.safe_load((imported/"metamodel.yaml").read_bytes())
        result=compare(original,recovered)
        assert result["status"]=="pass",result
        assert result["original"]["pairs"]==SPEC["expected_generated_pairs"]
        inv=inventory(recovered)
        for group in SPEC["groups"]:
            prefix=group["id"]+"_"
            assert len([ident for ident in inv["collections"]["elements"]["ids"]
                        if ident.startswith(prefix)])==group["count"]
        assert all(rule["id"] in inv["pairs"] for rule in SPEC["relationship_rules"])
        # Detect a same-count substitution: aggregate counts alone cannot catch it.
        tampered=copy.deepcopy(recovered)
        key=SPEC["relationship_rules"][0]["id"]
        relation=next(item for item in tampered["relationships"] if item["id"]==key)
        relation["allowed_typed_pairs"][0]["target"]["id"]="unknown_target"
        drift=compare(original,tampered)
        assert drift["status"]=="fail"
        assert any(x["kind"]=="relationship_pairs" and x.get("id")==key
                   for x in drift["losses"]),drift
        # Detect deletion of a type even when no relation pairs are involved.
        tampered=copy.deepcopy(recovered)
        tampered["elements"]=[e for e in tampered["elements"] if e["id"]!=generated[0]]
        removed=compare(original,tampered)
        assert any(x.get("id")==generated[0] and x["change"]=="missing"
                   for x in removed["losses"]),removed
        if "--typescript" in sys.argv:
            consumer=run("node",ROOT/"interop/typescript/dist/consumer.js",package)
            assert consumer.returncode==0,consumer.stderr[-3000:]
        # The report contains type IDs/digests/counts but not the full pair matrix.
        print(json.dumps({"audit":"generic-large-fixture","package":"MMP 1.1 candidate",
                          "status":result["status"],"inventory":result["original"],
                          "pair_groups":[{"id":id,"count":inv["pairs"][id]["count"],
                                          "digest":inv["pairs"][id]["digest"]}
                                         for id in sorted(inv["pairs"])],
                          "negative_controls":["pair_mutation_detected","type_deletion_detected"],
                          "limits":["synthetic fixture","no external semantic certification"]},
                         ensure_ascii=False,sort_keys=True))
if __name__=="__main__":
    main()
