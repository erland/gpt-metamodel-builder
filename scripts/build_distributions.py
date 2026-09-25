#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root', default='.')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--version', required=True)
    a=ap.parse_args(); root=Path(a.project_root).resolve()
    subprocess.run([
        sys.executable, str(root/'scripts/build_release.py'),
        '--project-root', str(root), '--output-dir', a.output_dir,
        '--version', a.version, '--skip-ci'
    ], check=True)
    return 0

if __name__=='__main__': raise SystemExit(main())
