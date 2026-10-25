#!/usr/bin/env python3
"""CORE-016 schema, typed-reference and legacy migration smoke tests."""
import json, shutil, subprocess, sys, tempfile
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from referencing import Registry,Resource

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_semantics import validate

with tempfile.TemporaryDirectory() as tmp:
    model=Path(tmp)/"model";shutil.copytree(ROOT/"examples/architecture-lite",model)
    f=model/"metamodel.yaml";original=f.read_bytes();m=yaml.safe_load(original)
    schema=json.loads((ROOT/"schemas/metamodel.schema.json").read_text())
    common=json.loads((ROOT/"schemas/common-definitions.schema.json").read_text())
    registry=Registry().with_resource(common["$id"],Resource.from_contents(common))
    def check_schema():
        Draft202012Validator(schema,registry=registry).validate(m)
    check_schema()
    assert not validate(model).errors
    m["junctions"]=[{"id":"j_core016","name":"Conjunction"}]
    rel=m["relationships"][0];source=rel["source"]["types"][0]
    rel["source"]["typed_refs"]=[{"kind":"element","id":v} for v in rel["source"]["types"]]+[{"kind":"junction","id":"j_core016"}]
    rel["target"]["typed_refs"]=[{"kind":"element","id":v} for v in rel["target"]["types"]]+[{"kind":"relationship","id":rel["id"]}]
    check_schema()
    f.write_text(yaml.safe_dump(m,sort_keys=False))
    report=validate(model)
    assert not report.errors,report.errors
    p=subprocess.run([sys.executable,str(ROOT/"scripts/export_mmp.py"),"--candidate-1-1","--model-dir",str(model),"--output",str(Path(tmp)/"unsupported.zip")],capture_output=True,text=True)
    assert p.returncode!=0 and "CORE-016 not_supported" in p.stderr,p.stderr
    assert not (Path(tmp)/"unsupported.zip").exists()
    rel["source"]["typed_refs"].append({"kind":"element","id":source})
    f.write_text(yaml.safe_dump(m,sort_keys=False))
    assert "duplicate_typed_endpoint" in {err["code"] for err in validate(model).errors}
    rel["source"]["typed_refs"].pop()
    rel["source"]["typed_refs"][-1]["id"]="missing_junction"
    f.write_text(yaml.safe_dump(m,sort_keys=False))
    assert "unknown_typed_endpoint" in {err["code"] for err in validate(model).errors}
    rel["source"]["typed_refs"][-1]["id"]="j_core016"
    rel["source"]["types"]=[]
    f.write_text(yaml.safe_dump(m,sort_keys=False))
    assert "typed_endpoint_legacy_mismatch" in {err["code"] for err in validate(model).errors}
    f.write_bytes(original)
    assert not validate(model).errors
    assert f.read_bytes()==original
print("CORE-016 canonical typed endpoints PASS")
