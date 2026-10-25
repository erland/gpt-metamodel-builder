#!/usr/bin/env python3
"""Build a distinct package-level Core subset suite; do not change v1 baseline."""
import hashlib,io,json,zipfile
import yaml

def create(base):
    with zipfile.ZipFile(io.BytesIO(base)) as z:
        original={n:z.read(n) for n in z.namelist()}
    cases=[
      ("diamond-inheritance","accept","CORE-003",{"application":["owner","status"],"platform":["owner","status"],"special_application":["owner","status"]}),
      ("unknown-property-set","reject","CORE-005",None),
      ("unknown-relation-parent","reject","CORE-002",None),
      ("inverted-endpoint-cardinality-v1","accept","CORE-007",None)
    ]
    result={}
    for ident,expected,req,semantic in cases:
        files=dict(original)
        manifest=yaml.safe_load(files["manifest.yaml"])
        model=yaml.safe_load(files["canonical/metamodel.yaml"])
        if ident=="diamond-inheritance":
            model["elements"].append({"id":"special_application","name":"Special Application","kind":"artifact","extends":["application","platform"],"property_sets":["lifecycle"]})
        if ident=="unknown-property-set":
            model["elements"][0]["property_sets"]=["missing_set"]
        if ident=="unknown-relation-parent":
            model["relationships"][0]["extends"]=["unknown_relation"]
        if ident=="inverted-endpoint-cardinality-v1":
            model["relationships"][0]["source"]["cardinality"]="3..1"
        files["canonical/metamodel.yaml"]=yaml.safe_dump(model,sort_keys=False,allow_unicode=True).encode()
        for entry in manifest["files"]:
            if entry["path"] in files:
                entry["sha256"]=hashlib.sha256(files[entry["path"]]).hexdigest()
        files["manifest.yaml"]=yaml.safe_dump(manifest,sort_keys=False,allow_unicode=True).encode()
        target=io.BytesIO()
        with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for name,content in sorted(files.items()):
                info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,content)
        data=target.getvalue()
        name="conformance/packages-semantic/"+ident+".mmp.zip"
        result[name]=data
    entries=[]
    for ident,expected,req,semantic in cases:
        name="conformance/packages-semantic/"+ident+".mmp.zip"
        entries.append({"id":ident,"expected":expected,"requirement":req,"package":name,
                        "sha256":hashlib.sha256(result[name]).hexdigest(),
                        "effective_properties":semantic,
                        "note":"Schema-valid legacy MMP 1.0.0; inverted range is reserved for opt-in strict profile" if ident=="inverted-endpoint-cardinality-v1" else ""})
    result["conformance/package-semantic-manifest.json"]=(json.dumps({"suite_version":"0.1.0","format_version":"1.0.0","kind":"package-core-subset","cases":entries},indent=2)+"\n").encode()
    return result
