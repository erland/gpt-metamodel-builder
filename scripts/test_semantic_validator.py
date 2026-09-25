#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate_semantics.py'

def run(path: Path):
    return subprocess.run([sys.executable, str(VALIDATOR), str(path)], capture_output=True, text=True)

def main():
    valid = run(ROOT / 'examples' / 'architecture-lite')
    if valid.returncode != 0:
        print(valid.stdout); print(valid.stderr, file=sys.stderr)
        raise SystemExit('Valid reference model was rejected')
    failures=[]
    for case in sorted((ROOT/'tests'/'semantic-invalid').iterdir()):
        if not case.is_dir(): continue
        r=run(case)
        if r.returncode == 0:
            failures.append(case.name)
    if failures:
        raise SystemExit('Invalid semantic cases accepted: ' + ', '.join(failures))
    print('Semantic validator tests OK: 1 valid + 7 invalid cases')

if __name__ == '__main__': main()
