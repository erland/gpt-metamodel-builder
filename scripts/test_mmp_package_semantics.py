#!/usr/bin/env python3
import argparse,hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument("kit",type=Path);args=parser.parse_args()
with zipfile.ZipFile(args.kit) as z:
    manifest=json.loads(z.read("conformance/package-semantic-manifest.json"))
    assert manifest["suite_version"]=="0.1.0"
    with tempfile.TemporaryDirectory() as td:
        for case in manifest["cases"]:
            blob=z.read(case["package"])
            assert hashlib.sha256(blob).hexdigest()==case["sha256"]
            file=Path(td)/(case["id"]+".zip");file.write_bytes(blob)
            run=subprocess.run([sys.executable,str(ROOT/"interop/mmp_v1_consumer.py"),str(file)],capture_output=True,text=True,timeout=30)
            actual="accept" if run.returncode==0 else "reject"
            assert actual==case["expected"],(case["id"],actual,run.stderr)
            if case["effective_properties"] is not None:
                data=json.loads(run.stdout)["effective_properties"]["elements"]
                for typ,props in case["effective_properties"].items():
                    assert data[typ]["properties"]==props,(case["id"],typ,data[typ])
            print("PASS",case["id"])
print("PASS: package-level Python Core subset (not full Core conformance)")
