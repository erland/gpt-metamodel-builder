#!/usr/bin/env python3
"""Build a tool-neutral MMP v1 specification and conformance kit."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path
import yaml
from mmp_conformance_fixtures import bundle as conformance_bundle
from mmp_package_semantic_fixtures import create as semantic_packages

ROOT=Path(__file__).resolve().parents[1]
FORMAT_VERSION="1.0.0"
SCHEMAS=("mmp-manifest-v1","metamodel","properties","constraints","viewpoints","notation","provenance","version","guidance","common-definitions","mmp-conformance-declaration-v1")
ZIP_DATE=(1980,1,1,0,0,0)

def package(output:Path):
    with tempfile.TemporaryDirectory() as work:
        tmp=Path(work); model=tmp/"model"
        shutil.copytree(ROOT/"examples/architecture-lite",model)
        mm=model/"metamodel.yaml"
        data=yaml.safe_load(mm.read_text(encoding="utf-8"))
        data["metamodel"]["namespace"]="https://example.org/mmp/architecture-lite"
        mm.write_text(yaml.safe_dump(data,sort_keys=False,allow_unicode=True),encoding="utf-8")
        example=tmp/"architecture-example.mmp.zip"
        cmd=[sys.executable,str(ROOT/"scripts/export_mmp.py"),"--model-dir",str(model),"--output",str(example),"--producer-version","mmp-kit"]
        env={**os.environ,"SOURCE_DATE_EPOCH":"1792843200"}
        subprocess.run(cmd,check=True,capture_output=True,env=env)
        entries={
            "README.md":(ROOT/"mmp-kit/README.md").read_bytes(),
            "specification/mmp-v1.md":(ROOT/"docs/mmp-v1-contract.md").read_bytes(),
            "specification/implementation-guide.md":(ROOT/"mmp-kit/implementation-guide.md").read_bytes(),
            "specification/package-level-conformance.md":(ROOT/"docs/mmp-package-level-conformance.md").read_bytes(),
            "specification/strict-core-package-profile.md":(ROOT/"docs/mmp-strict-core-package-profile.md").read_bytes(),
            "specification/strict-core-coverage.md":(ROOT/"docs/mmp-strict-core-coverage.md").read_bytes(),
            "conformance/strict-core-coverage-v1.json":(ROOT/"conformance/strict-core-coverage-v1.json").read_bytes(),
            "conformance/mmp-version-decision-v1.json":(ROOT/"conformance/mmp-version-decision-v1.json").read_bytes(),
            "specification/version-compatibility-decision.md":(ROOT/"docs/mmp-version-compatibility-decision.md").read_bytes(),
            "specification/conformance.md":(ROOT/"mmp-kit/conformance.md").read_bytes(),
            "specification/conformance-profiles-proposal.md":(ROOT/"docs/mmp-conformance-profiles-proposal.md").read_bytes(),
            "examples/mmp-consumer-conformance.json":(ROOT/"examples/mmp-consumer-conformance.json").read_bytes(),
            "reference-implementation/mmp_v1_consumer.py":(ROOT/"interop/mmp_v1_consumer.py").read_bytes(),
            "examples/architecture-example.mmp.zip":example.read_bytes(),
            "conformance/effective-properties-v1.json":(ROOT/"interop/effective-properties-v1.json").read_bytes(),
            "conformance/cardinality-v1.json":(ROOT/"interop/cardinality-v1.json").read_bytes(),
            "conformance/default-values-v1.json":(ROOT/"interop/default-values-v1.json").read_bytes(),
            "conformance/relationship-semantics-v1.json":(ROOT/"interop/relationship-semantics-v1.json").read_bytes(),
            "conformance/version-extension-v1.json":(ROOT/"interop/version-extension-v1.json").read_bytes(),
            "specification/version-extensions-proposal.md":(ROOT/"docs/mmp-version-extensions.md").read_bytes(),
            "specification/mmp-1-1-readiness-review.md":(ROOT/"docs/mmp-1-1-readiness-review.md").read_bytes(),
            "conformance/mmp-1-1-readiness.json":(ROOT/"conformance/mmp-1-1-readiness.json").read_bytes(),
            "conformance/relationship-inheritance-v1.json":(ROOT/"interop/relationship-inheritance-v1.json").read_bytes(),
            "conformance/required-policy-v1.json":(ROOT/"interop/required-policy-v1.json").read_bytes(),
            "conformance/canonical-values-v1.json":(ROOT/"interop/canonical-values-v1.json").read_bytes(),
            "conformance/extension-negotiation-v1.json":(ROOT/"interop/extension-negotiation-v1.json").read_bytes(),
            "conformance/core-semantic-suite-v1.json":(ROOT/"conformance/core-semantic-suite-v1.json").read_bytes(),
            "conformance/run_core_semantic_suite.py":(ROOT/"scripts/run_mmp_core_semantic_suite.py").read_bytes(),
            "specification/extension-negotiation-proposal.md":(ROOT/"docs/mmp-extension-negotiation.md").read_bytes(),
            "specification/canonical-values-policy.md":(ROOT/"docs/mmp-canonical-values-policy.md").read_bytes(),
            "specification/required-minimum-policy.md":(ROOT/"docs/mmp-required-minimum-policy.md").read_bytes(),
            "specification/relation-inheritance-policy.md":(ROOT/"docs/mmp-relation-inheritance-policy.md").read_bytes(),
            "specification/relationship-semantics-proposal.md":(ROOT/"docs/mmp-relationship-semantics.md").read_bytes(),
            "specification/default-value-semantics-proposal.md":(ROOT/"docs/mmp-default-value-semantics.md").read_bytes(),
            "specification/cardinality-semantics-proposal.md":(ROOT/"docs/mmp-cardinality-semantics.md").read_bytes(),
        }
        entries.update(conformance_bundle(example.read_bytes()))
        entries.update(semantic_packages(example.read_bytes()))
        entries["conformance/run_suite.py"]=(ROOT/"scripts/mmp_conformance_runner.py").read_bytes()
        for name in SCHEMAS:
            filename=name+".schema.json"
            entries["schemas/"+filename]=(ROOT/"schemas"/filename).read_bytes()
        checksums="".join(f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name,content in sorted(entries.items()))
        entries["SHA256SUMS.txt"]=checksums.encode()
        output.parent.mkdir(parents=True,exist_ok=True)
        if output.exists(): raise FileExistsError(output)
        with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for name,content in sorted(entries.items()):
                info=zipfile.ZipInfo(name,ZIP_DATE)
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,content)
        return output

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,required=True);args=ap.parse_args()
    print(package(args.output))
if __name__=="__main__":main()
