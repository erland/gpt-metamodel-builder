#!/usr/bin/env python3
"""Validate built standalone MMP kit integrity and sample interoperability."""
import argparse,hashlib,os,subprocess,sys,tempfile,zipfile
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--archive",type=Path,required=True);a=ap.parse_args()
    with zipfile.ZipFile(a.archive) as z:
        names=set(z.namelist())
        assert z.testzip() is None
        manifest=z.read("SHA256SUMS.txt").decode()
        accounted=set()
        for line in manifest.splitlines():
            sha,name=line.split("  ",1)
            assert name in names and hashlib.sha256(z.read(name)).hexdigest()==sha,name
            accounted.add(name)
        assert accounted==names-{"SHA256SUMS.txt"}
        for name in ["README.md","specification/mmp-v1.md","specification/implementation-guide.md",
                     "specification/conformance.md","schemas/mmp-manifest-v1.schema.json",
                     "reference-implementation/mmp_v1_consumer.py","examples/architecture-example.mmp.zip"]:
            assert name in names,name
        with tempfile.TemporaryDirectory() as td:
            z.extract("reference-implementation/mmp_v1_consumer.py",td)
            z.extract("examples/architecture-example.mmp.zip",td)
            base=Path(td)
            test=subprocess.run([sys.executable,str(base/"reference-implementation/mmp_v1_consumer.py"),
                   str(base/"examples/architecture-example.mmp.zip")],capture_output=True,text=True)
            assert test.returncode==0,test.stderr
            assert '"elements"' in test.stdout and '"relationships"' in test.stdout
            z.extract("conformance/run_suite.py",td)
            suite=subprocess.run([sys.executable,str(base/"conformance/run_suite.py"),
                  "--kit",str(a.archive.resolve()),"--consumer",
                  str(base/"reference-implementation/mmp_v1_consumer.py")],capture_output=True,text=True)
            assert suite.returncode==0,suite.stdout+"\n"+suite.stderr
            assert "9/9 PASS" in suite.stdout,suite.stdout
    print("MMP specification kit PASS: checksums, files, independent example consumption")

if __name__=="__main__":main()
