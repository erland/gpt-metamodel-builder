#!/usr/bin/env python3
"""Migration target contract gate (not a distribution build test)."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
migration = yaml.safe_load((ROOT / "migration/runtime-1.6.31.yaml").read_text(encoding="utf-8"))
project = yaml.safe_load((ROOT / "gpt-project.yaml").read_text(encoding="utf-8"))
expected = {
    "chat": ("chatgpt_chat", "chat_zip", "chat", "chat_zip"),
    "plugin": ("openai_plugin", "plugin", "plugin", "plugin_zip"),
    "claude_project": ("claude_project", "claude", "claude", "claude_project_zip"),
    "claude_skills": ("claude_skills", "claude", "claude_skills", "claude_skills_zip"),
    "opencode": ("opencode", "opencode", "opencode", "opencode_zip"),
}
assert migration["migration"]["engine_version"] == "1.6.31"
assert migration["migration"]["legacy_build_active"] is True
assert set(migration["runtimes"]) == set(expected)
for key, values in expected.items():
    actual = migration["runtimes"][key]
    assert tuple(actual[name] for name in ("runtime_id", "runtime_key", "builder", "artifact_type")) == values, key
    assert actual["enabled"] is True
assert migration["disabled"] == ["chatgpt_custom"]
assert project["instructions"]["mode"] == "modular_skills"
assert (ROOT / project["instructions"]["core"]).is_file()
assert len(project["skills"]["definitions"]) == 4
assert len(project["tools"]["tools"]) == 11
for skill in project["skills"]["definitions"]:
    assert (ROOT / skill["source"]).is_file(), skill["id"]
    for kind in ("references", "assets", "scripts"):
        for path in skill[kind]:
            assert (ROOT / path).exists() and ((ROOT / path).is_file() or (kind == "assets" and (ROOT / path).is_dir())), path
print("Migration runtime 1.6.31 contract: PASS (declarative, not build verification)")
