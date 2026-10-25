#!/usr/bin/env python3
"""Ensure PR concurrency cancels superseded commits, not releases."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ("ci.yml","mmp-typescript.yml","gpt-byggaren-engine.yml"):
    workflow=(root/".github/workflows"/name).read_text()
    assert "github.workflow" in workflow, name
    assert "github.event.pull_request.number || github.ref" in workflow, name
    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in workflow, name
    assert "pull_request:" in workflow, name
print("PASS: superseded PR checks cancel without cancelling manual or release runs")
