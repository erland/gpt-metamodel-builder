#!/usr/bin/env python3
"""Generate deterministic, offline MMP conformance fixtures and a machine-readable manifest."""
from __future__ import annotations
import hashlib, io, json, zipfile
from pathlib import Path
import yaml

STAMP=(1980,1,1,0,0,0)
CASES=[
 ("valid-baseline","accept","Unchanged MMP v1 example package"),
 ("invalid-sha256","reject","Manifest hash does not match canonical content"),
 ("invalid-duplicate-type-id","reject","Duplicate element type identifier"),
 ("invalid-unknown-parent","reject","Unknown extends reference"),
 ("invalid-inheritance-cycle","reject","Cyclic element type inheritance"),
 ("invalid-unknown-endpoint","reject","Unknown relationship endpoint type"),
 ("invalid-schema-required","reject","Missing required schema_version field"),
 ("invalid-format-version","reject","Unsupported MMP package format version"),
 ("invalid-extra-file","reject","Undeclared extra ZIP member"),
]
def create(base:bytes)->dict[str,bytes]:
    with zipfile.ZipFile(io.BytesIO(base)) as z:
        original={name:z.read(name) for name in z.namelist()}
    produced={}
    for ident,_,_ in CASES:
        data=dict(original)
        manifest=yaml.safe_load(data["manifest.yaml"])
        def change_doc(path,mutate):
            doc=yaml.safe_load(data[path]);mutate(doc)
            data[path]=yaml.safe_dump(doc,sort_keys=False,allow_unicode=True).encode("utf-8")
        if ident=="invalid-sha256":
            data["canonical/metamodel.yaml"]+=b"\n# tampered\n"
        if ident=="invalid-duplicate-type-id":
            def duplicate(d):
                copy=dict(d["elements"][0]);d["elements"].append(copy)
            change_doc("canonical/metamodel.yaml",duplicate)
        if ident=="invalid-unknown-parent":
            change_doc("canonical/metamodel.yaml",lambda d:d["elements"][0].update({"extends":["unknown-parent"]}))
        if ident=="invalid-inheritance-cycle":
            def cycle(d):
                first=d["elements"][0]["id"]
                d["elements"][0]["extends"]=[first]
            change_doc("canonical/metamodel.yaml",cycle)
        if ident=="invalid-unknown-endpoint":
            change_doc("canonical/metamodel.yaml",lambda d:d["relationships"][0]["source"].update({"types":["unknown-element"]}))
        if ident=="invalid-schema-required":
            change_doc("canonical/properties.yaml",lambda d:d.pop("schema_version"))
        if ident=="invalid-format-version":
            manifest["package_format_version"]="9.0.0"
        if ident=="invalid-extra-file":
            data["unexpected.txt"]=b"Undeclared"
        if ident not in ("invalid-sha256","invalid-extra-file"):
            for item in manifest["files"]:
                if item["path"] in data:
                    item["sha256"]=hashlib.sha256(data[item["path"]]).hexdigest()
            data["manifest.yaml"]=yaml.safe_dump(manifest,sort_keys=False,allow_unicode=True).encode("utf-8")
        output=io.BytesIO()
        with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for name,raw in sorted(data.items()):
                info=zipfile.ZipInfo(name,STAMP)
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,raw)
        produced[ident]=output.getvalue()
    return produced

def bundle(base:bytes)->dict[str,bytes]:
    packages=create(base)
    manifest={"suite_version":"1.0.0","format_version":"1.0.0",
      "status":"baseline subset; not a complete MMP Core certification",
      "cases":[{"id":ident,"profile":"mmp-core","expected":expected,"description":description,
                "package":f"conformance/packages/{ident}.mmp.zip",
                "sha256":hashlib.sha256(packages[ident]).hexdigest()}
               for ident,expected,description in CASES]}
    out={f"conformance/packages/{ident}.mmp.zip":raw for ident,raw in packages.items()}
    out["conformance/test-manifest.json"]=(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n").encode()
    return out
