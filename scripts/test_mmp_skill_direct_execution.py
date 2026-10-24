#!/usr/bin/env python3
"""Run MMP tools from extracted, isolated Plugin and Claude Skills archives."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
import yaml

ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    result=subprocess.run([sys.executable,*map(str,args)],capture_output=True,text=True,
                          env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"})
    if result.returncode:
        raise AssertionError(f"{args}: {result.stdout}\n{result.stderr}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dist",type=Path,default=Path("dist"))
    args=ap.parse_args()
    for runtime in ("plugin","claude-skills"):
        archives=list(args.dist.glob(f"metamodel-builder-{runtime}-*.zip"))
        assert len(archives)==1,archives
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            with zipfile.ZipFile(archives[0]) as z:
                z.extractall(base)
            skill=base/"skills/metamodellering"
            for item in ("schemas/mmp-manifest-v1.schema.json","schemas/metamodel.schema.json"):
                assert (skill/"assets"/item).is_file(),item
            assert (skill/"assets/metamodel/guidance.yaml").is_file()
            source=base/"external-model"
            shutil.copytree(ROOT/"examples/architecture-lite",source)
            file=source/"metamodel.yaml"
            model=yaml.safe_load(file.read_text())
            model["metamodel"]["namespace"]="https://example.org/metamodels/archlite"
            file.write_text(yaml.safe_dump(model,sort_keys=False,allow_unicode=True))
            scripts=skill/"scripts"
            run(scripts/"validate_canonical_schema.py","--model-dir",source)
            package=base/"model.mmp.zip"
            run(scripts/"export_mmp.py","--model-dir",source,"--output",package)
            run(scripts/"import_mmp.py","validate",package)
            target=base/"reimported"
            run(scripts/"import_mmp.py","import",package,"--output",target)
            for name in ("metamodel.yaml","properties.yaml","version.yaml"):
                assert (source/name).read_bytes()==(target/name).read_bytes()
        print(f"PASS: {runtime} Skill scripts execute against external model without Engine ZIP")

if __name__=="__main__":
    main()
