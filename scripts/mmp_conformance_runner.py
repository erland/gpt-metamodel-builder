#!/usr/bin/env python3
"""Execute a portable MMP conformance test manifest against a consumer CLI.

The consumer must take a package path and return exit code 0 for accept.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile, zipfile
from pathlib import Path

def run(kit:Path,consumer:Path)->dict:
    with zipfile.ZipFile(kit) as z:
        manifest=json.loads(z.read("conformance/test-manifest.json"))
        assert manifest["suite_version"]=="1.0.0"
        results=[]
        with tempfile.TemporaryDirectory() as td:
            for case in manifest["cases"]:
                name=case["package"]
                assert name.startswith("conformance/packages/") and ".." not in name
                raw=z.read(name)
                assert hashlib.sha256(raw).hexdigest()==case["sha256"],name
                path=Path(td)/Path(name).name
                path.write_bytes(raw)
                invocation=[sys.executable,str(consumer),str(path)] if consumer.suffix==".py" else [str(consumer),str(path)]
                p=subprocess.run(invocation,capture_output=True,text=True,timeout=30)
                got="accept" if p.returncode==0 else "reject"
                results.append({"id":case["id"],"expected":case["expected"],"actual":got,"passed":case["expected"]==got})
        return {"suite_version":manifest["suite_version"],"consumer":str(consumer),
                "passed":sum(int(x["passed"]) for x in results),"total":len(results),"results":results}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--kit",required=True,type=Path)
    ap.add_argument("--consumer",required=True,type=Path)
    ap.add_argument("--json-out",type=Path)
    a=ap.parse_args()
    report=run(a.kit,a.consumer.resolve())
    if a.json_out:
        a.json_out.write_text(json.dumps(report,indent=2)+"\n")
    print(f"MMP conformance: {report['passed']}/{report['total']} PASS")
    for item in report["results"]:
        print(f"{'PASS' if item['passed'] else 'FAIL'} {item['id']}: expected {item['expected']}, got {item['actual']}")
    return 0 if report["passed"]==report["total"] else 1
if __name__=="__main__":raise SystemExit(main())
