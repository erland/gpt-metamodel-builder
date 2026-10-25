#!/usr/bin/env python3
"""CORE-015 canonical pair validation and lossless-export safety smoke."""
import copy, shutil, tempfile, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_semantics import validate

with tempfile.TemporaryDirectory() as tmp:
    d=Path(tmp)/"model";shutil.copytree(ROOT/"examples/architecture-lite",d)
    p=d/"metamodel.yaml";original=p.read_bytes();data=yaml.safe_load(original)
    rel=data["relationships"][0]
    src=rel["source"]["types"][0];dst=rel["target"]["types"][0]
    rel["allowed_type_pairs"]=[{"source":src,"target":dst}]
    p.write_text(yaml.safe_dump(data,sort_keys=False))
    report=validate(d)
    assert not report.errors,report.errors
    exported=subprocess.run([sys.executable,str(ROOT/"scripts/export_mmp.py"),"--model-dir",str(d),"--output",str(Path(tmp)/"blocked.zip")],capture_output=True,text=True)
    assert exported.returncode and "CORE-015 not_supported" in exported.stderr,exported.stderr
    assert not (Path(tmp)/"blocked.zip").exists()
    rel["allowed_type_pairs"].append({"source":src,"target":dst})
    p.write_text(yaml.safe_dump(data,sort_keys=False))
    assert "duplicate_allowed_pair" in [x["code"] for x in validate(d).errors]
    rel["allowed_type_pairs"]=[{"source":"missing_type","target":dst}]
    p.write_text(yaml.safe_dump(data,sort_keys=False))
    assert "unknown_pair_source" in [x["code"] for x in validate(d).errors]
    p.write_bytes(original)
    assert not validate(d).errors
print("CORE-015 foundation PASS")
