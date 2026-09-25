#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'examples/architecture-lite'
GEN=ROOT/'scripts/generate_documentation.py'
with tempfile.TemporaryDirectory() as td:
    a=Path(td)/'a.md'; b=Path(td)/'b.md'
    subprocess.check_call([sys.executable,str(GEN),str(MODEL),str(a)])
    subprocess.check_call([sys.executable,str(GEN),str(MODEL),str(b)])
    x=a.read_bytes(); y=b.read_bytes()
    assert x==y, 'documentation generation is not deterministic'
    txt=x.decode('utf-8')
    required=['# Architecture Lite – metamodell','## Elementtyper','capability','## Relationstyper','platform_supports_application','## Egenskaper','lifecycle_status','## Constraints','capability_has_owner','## Viewpoints','Capability Map','## Notation','## Provenance','user_design','## Versionsinformation','1.0.0']
    missing=[s for s in required if s not in txt]
    assert not missing, f'missing expected documentation fragments: {missing}'
print('Documentation generator tests OK')
