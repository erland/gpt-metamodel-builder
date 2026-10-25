#!/usr/bin/env python3
"""CORE-016 typed exact pairs canonical regression, including legacy preservation."""
import shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_semantics import validate

with tempfile.TemporaryDirectory() as td:
    path=Path(td)/"model";shutil.copytree(ROOT/"examples/architecture-lite",path)
    f=path/"metamodel.yaml";original=f.read_bytes();data=yaml.safe_load(original)
    rel=data["relationships"][0]
    data["junctions"]=[{"id":"core016_join","name":"AND"}]
    rel["source"]["typed_refs"]=[{"kind":"element","id":ident} for ident in rel["source"]["types"]]+[{"kind":"junction","id":"core016_join"}]
    rel["target"]["typed_refs"]=[{"kind":"element","id":ident} for ident in rel["target"]["types"]]+[{"kind":"relationship","id":rel["id"]}]
    pair={"source":{"kind":"junction","id":"core016_join"},"target":{"kind":"relationship","id":rel["id"]}}
    rel["allowed_typed_pairs"]=[pair]
    def save():f.write_text(yaml.safe_dump(data,sort_keys=False))
    save()
    assert not validate(path).errors,validate(path).errors
    p=subprocess.run([sys.executable,str(ROOT/"scripts/export_mmp.py"),"--candidate-1-1","--model-dir",str(path),"--output",str(Path(td)/"out.zip")],capture_output=True,text=True)
    assert p.returncode!=0 and "CORE-016 not_supported" in p.stderr,p.stderr
    assert not (Path(td)/"out.zip").exists()
    rel["allowed_typed_pairs"].append(dict(pair))
    save()
    assert "duplicate_allowed_typed_pair" in {x["code"] for x in validate(path).errors}
    rel["allowed_typed_pairs"].pop()
    rel["allowed_typed_pairs"][0]["source"]["id"]="unknown"
    save()
    assert "typed_pair_outside_endpoints" in {x["code"] for x in validate(path).errors}
    rel["allowed_typed_pairs"][0]["source"]["id"]="core016_join"
    rel["allowed_type_pairs"]=[{"source":rel["source"]["types"][0],"target":rel["target"]["types"][0]}]
    save()
    assert "mixed_pair_profiles" in {x["code"] for x in validate(path).errors}
    f.write_bytes(original)
    assert not validate(path).errors
    assert f.read_bytes()==original
print("CORE-016 typed pair foundation PASS")
