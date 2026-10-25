#!/usr/bin/env python3
"""Prevent accidental publication or premature build in tagged verification."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/".github/workflows/mmp11-tagged-verification.yml"
s=path.read_text()
assert "workflow_dispatch:" in s and "release:" not in s and "push:" not in s
assert '[[ "$GITHUB_REF" == refs/tags/* ]]' in s
assert "contents: read" in s
assert "verify_mmp_11_release_artifact.py" in s
assert "--typescript" in s
assert s.index("python scripts/run_ci.py") < s.index("python scripts/build_mmp_specification_1_2.py")
assert "npm install --no-audit --no-fund" in s and "npm ci " not in s
assert "actions/upload-artifact@v4" in s
assert "gh release" not in s and "contents: write" not in s
print("Tagged verification workflow safety PASS")
