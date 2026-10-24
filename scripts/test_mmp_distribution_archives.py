#!/usr/bin/env python3
"""Assert MMP tools are shipped in real runtime ZIPs and offline Engine ZIP."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

SCRIPTS=("export_mmp.py","import_mmp.py")
ENGINE_SCRIPTS=(*SCRIPTS,"test_mmp_export.py","test_mmp_import.py","test_mmp_interop.py",
                "test_mmp_consumer_security.py","test_mmp_consumer_semantics.py",
                "test_mmp_identity_evolution.py")
ENGINE_EXTRAS=("schemas/mmp-manifest-v1.schema.json","interop/mmp_v1_consumer.py",
               "docs/mmp-v1-contract.md")


def only(dist: Path, fragment: str) -> Path:
    matches=list(dist.glob(f"metamodel-builder-{fragment}-*.zip"))
    if len(matches)!=1:
        raise AssertionError(f"Expected exactly one {fragment} ZIP, found {len(matches)}")
    return matches[0]


def runtime(path: Path):
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        for name in SCRIPTS:
            expected=f"skills/metamodellering/scripts/{name}"
            assert expected in names, f"{path.name}: missing {expected}"
            assert z.read(expected).startswith(b"#!/usr/bin/env python3")
        skill=z.read("skills/metamodellering/SKILL.md").decode("utf-8")
        assert "MMP" in skill and "Engine" in skill, f"{path.name}: handoff instructions absent"
        contract=json.loads(z.read("runtime-contract.json"))
        assert contract.get("runtime_id") in ("openai_plugin","claude_skills")


def engine(path: Path):
    with zipfile.ZipFile(path) as z:
        names=set(z.namelist())
        manifest=json.loads(z.read("engine-package.json"))
        assert manifest["engine_id"]=="metamodel-builder"
        assert manifest["entrypoint"]=="scripts/selftest_metamodel_engine.py"
        assert set(manifest["files"])==names-{"engine-package.json"}
        for name, sha in manifest["files"].items():
            assert hashlib.sha256(z.read(name)).hexdigest()==sha, f"Checksum mismatch: {name}"
        for name in (*[f"scripts/{p}" for p in ENGINE_SCRIPTS],*ENGINE_EXTRAS):
            assert name in names, f"{path.name}: missing {name}"
        selftest=z.read("scripts/selftest_metamodel_engine.py").decode()
        for name in ENGINE_SCRIPTS[2:]:
            assert name in selftest, f"Engine selftest lacks {name}"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dist",type=Path,default=Path("dist"))
    args=ap.parse_args()
    runtime(only(args.dist,"plugin"))
    runtime(only(args.dist,"claude-skills"))
    engine(only(args.dist,"engine"))
    print("PASS: MMP runtime archives contain both scripts; Engine contains checksummed support and test suite")

if __name__=="__main__":
    main()
