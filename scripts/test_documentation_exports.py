#!/usr/bin/env python3
from pathlib import Path
import shutil, subprocess, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'docs'; cmd=[sys.executable,str(ROOT/'scripts/export_documentation.py'),str(ROOT/'examples/architecture-lite'),str(out),'--document','all','--format','all']; subprocess.run(cmd,check=True)
        expected=[f'{d}.{e}' for d in ['reference','modeling-guide','quick-reference'] for e in ['md','confluence','pdf']]
        missing=[n for n in expected if not (out/n).is_file() or (out/n).stat().st_size==0]
        if missing: raise SystemExit('Missing outputs: '+repr(missing))
        guide=(out/'modeling-guide.md').read_text(encoding='utf-8')
        for phrase in ['Använd när','Använd inte när','Relationsguide','Modelleringsmönster','Antimönster','Vanliga frågor']:
            if phrase not in guide: raise SystemExit('Missing modeling guide section: '+phrase)
        conf=(out/'quick-reference.confluence').read_text(encoding='utf-8')
        if 'h1.' not in conf or '||' not in conf: raise SystemExit('Confluence markup missing expected constructs')
        if (out/'modeling-guide.pdf').read_bytes()[:4] != b'%PDF': raise SystemExit('PDF signature missing')
    print('Documentation export OK: 3 document types x 3 formats')
if __name__=='__main__': main()
