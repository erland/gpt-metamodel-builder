#!/usr/bin/env python3
"""Run MMP semantic golden vectors with explicit per-language evidence.

A passing helper suite does NOT establish full MMP Core conformance.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"conformance/core-semantic-suite-v1.json"
READINESS=ROOT/"conformance/mmp-1-1-readiness.json"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--typescript",action="store_true",help="Run compiled Node 22 tests as well as Python")
    parser.add_argument("--json-out",type=Path)
    args=parser.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    readiness=json.loads(READINESS.read_text(encoding="utf-8"))
    assert manifest["suite_version"]=="0.1.0"
    assert manifest["release_claim"]=="not_ready" and readiness["overall"]=="not_ready"
    reqs={r["id"]:r for r in readiness["requirements"]}
    assert len(reqs)==14
    assert len({c["id"] for c in manifest["cases"]})==len(manifest["cases"])
    rows=[]
    for case in manifest["cases"]:
        assert case["scope"]=="helper-only"
        assert (ROOT/case["vector"]).is_file()
        assert all(ref in reqs for ref in case["requirements"])
        results={}
        invocations={"python":[sys.executable,str(ROOT/case["python"])]}
        if args.typescript:
            invocations["typescript"]=["node",str(ROOT/case["typescript"]),str(ROOT/case["vector"])]
        for language,command in invocations.items():
            assert Path(command[1]).is_file(),command
            proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
            results[language]={"status":"pass" if proc.returncode==0 else "fail","exit_code":proc.returncode}
            print(f'{case["id"]}: {language} {results[language]["status"]}',flush=True)
            if proc.returncode:
                print(proc.stdout+proc.stderr,file=sys.stderr)
        rows.append({"id":case["id"],"requirements":case["requirements"],"scope":case["scope"],"languages":results,
                     "status":"pass" if all(x["status"]=="pass" for x in results.values()) else "fail"})
    requirements={}
    for id,record in reqs.items():
        matches=[row for row in rows if id in row["requirements"]]
        requirements[id]={"readiness_status":record["status"],
           "semantic_subset":"pass" if matches and all(x["status"]=="pass" for x in matches) else "fail" if any(x["status"]=="fail" for x in matches) else "not_tested",
           "cases":[x["id"] for x in matches],
           "full_conformance":"not_verified"}
    report={"suite_version":manifest["suite_version"],"profile":"mmp-core","kind":manifest["kind"],
            "languages":["python","typescript"] if args.typescript else ["python"],
            "status":"pass" if all(r["status"]=="pass" for r in rows) else "fail",
            "full_core_conformance":"not_verified","release_decision":"NO-GO",
            "cases":rows,"requirements":requirements}
    if args.json_out:
        args.json_out.parent.mkdir(parents=True,exist_ok=True)
        args.json_out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f'Semantic subset: {sum(r["status"]=="pass" for r in rows)}/{len(rows)} PASS; full Core: NOT VERIFIED')
    return 0 if report["status"]=="pass" else 1

if __name__=="__main__":
    raise SystemExit(main())
