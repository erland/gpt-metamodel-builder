#!/usr/bin/env python3
"""Check the two runtime issues found in Metamodel Builder 1.2.0 packages."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zipfile


def archive(dist: Path, suffix: str) -> Path:
    found = sorted(dist.glob(f"metamodel-builder-{suffix}-*.zip"))
    if len(found) != 1:
        raise SystemExit(f"Expected one {suffix} archive, got {len(found)}")
    return found[0]


def validate(path: Path, *, claude: bool) -> None:
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        if z.testzip() is not None:
            raise ValueError(f"Corrupt archive: {path.name}")
        contract = json.loads(z.read("runtime-contract.json"))
        expected = "claude_skills" if claude else "openai_plugin"
        if contract.get("runtime_id") != expected:
            raise ValueError(f"{path.name}: wrong runtime_id")
        adapter = contract.get("adapter", {})
        if adapter.get("mode") != expected:
            raise ValueError(f"{path.name}: expected adapter.mode={expected}, got {adapter.get('mode')}")
        scripts = sorted(
            n for n in names
            if n.startswith("skills/") and n.endswith("/scripts/validate_workspace.py")
        )
        if scripts != ["skills/metamodellering/scripts/validate_workspace.py"]:
            raise ValueError(f"{path.name}: missing/duplicate workspace script: {scripts}")
        tools = contract.get("tools", {}).get("tools", [])
        if len(tools) != 11 or not any(t.get("id") == "validate-workspace" for t in tools):
            raise ValueError(f"{path.name}: wrong canonical tool contract")
        if claude and any("Plugin" in str(value) for value in adapter.get("parity_notes", {}).values()):
            raise ValueError(f"{path.name}: Plugin-specific parity notes remain")
    print(f"PASS: {path.name}: {expected}, 11 tools, workspace script")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", type=Path, default=Path("dist"))
    args = ap.parse_args()
    validate(archive(args.dist, "plugin"), claude=False)
    validate(archive(args.dist, "claude-skills"), claude=True)


if __name__ == "__main__":
    main()
