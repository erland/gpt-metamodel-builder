#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'scripts/validate_sparx_mapping.py'
CAN=ROOT/'examples/architecture-lite'
GOOD=CAN/'platforms/sparx-ea'
BAD=ROOT/'tests/sparx-mapping-invalid'
def run(adapter):
    return subprocess.run([sys.executable,str(V),'--project-root',str(ROOT),'--canonical',str(CAN),'--adapter',str(adapter)],capture_output=True,text=True)
r=run(GOOD)
if r.returncode!=0:
    print('Reference adapter should pass'); print(r.stdout); print(r.stderr); raise SystemExit(1)
failed=[]
for case in sorted(p for p in BAD.iterdir() if p.is_dir()):
    rr=run(case)
    if rr.returncode==0: failed.append(case.name)
if failed:
    print('Invalid adapters unexpectedly passed: '+', '.join(failed)); raise SystemExit(1)
print(f'Sparx mapping tests OK: 1 valid + {len(list(BAD.iterdir()))} invalid cases')
