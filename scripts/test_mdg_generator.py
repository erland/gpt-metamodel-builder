#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
CAN=ROOT/'examples/architecture-lite'; AD=CAN/'platforms/sparx-ea'

def sh(args):
    r=subprocess.run(args,cwd=ROOT,text=True,capture_output=True)
    if r.returncode: print(r.stdout); print(r.stderr,file=sys.stderr); raise SystemExit(r.returncode)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    a=Path(td)/'a.xml'; b=Path(td)/'b.xml'
    for out in (a,b): sh([sys.executable,'scripts/generate_sparx_mdg.py','--canonical',str(CAN),'--adapter',str(AD),'--output',str(out)])
    if digest(a)!=digest(b): raise SystemExit('Generator is not deterministic')
    sh([sys.executable,'scripts/validate_generated_mdg.py','--xml',str(a),'--canonical',str(CAN),'--adapter',str(AD)])
print('MDG generator tests: PASS')
