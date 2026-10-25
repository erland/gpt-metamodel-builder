#!/usr/bin/env python3
"""Static guardrail test for manual release candidate tag workflow."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/".github/workflows/create-release-candidate-tag.yml"
s=p.read_text()
for marker in ("workflow_dispatch:","contents: write","github.ref == 'refs/heads/main'",
               "v[0-9]+","-rc","Tag $TAG already exists","main moved",
               'gh api --method POST "repos/$REPO/git/refs"'):
 assert marker in s,marker
assert "release:" not in s and "gh release create" not in s
assert "git push --force" not in s
print("Manual release-candidate tag workflow safety PASS")
