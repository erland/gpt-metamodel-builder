#!/usr/bin/env python3
"""Check version-axis freeze without rewriting the shipped legacy kit."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
f=json.loads((ROOT/"conformance/mmp-11-version-scope-freeze.json").read_text())
kit=json.loads((ROOT/"mmp-kit/version.json").read_text())
assert f["package_format"]=="mmp"
assert f["target_package_format_version"]=="1.1.0"
assert kit["package_format_version"]==f["previous_package_format_version"]=="1.0.0"
assert kit["specification_kit_version"]==f["existing_specification_kit_version"]=="1.1.0"
assert f["next_specification_kit_version"] not in (f["existing_specification_kit_version"],f["target_package_format_version"])
assert f["release_gate"].startswith("NO_GO")
assert len({(c["id"],c["version"]) for c in f["supported_capabilities"]})==len(f["supported_capabilities"])
for p in f["evidence"].values():assert (ROOT/p).is_file(),p
print("MMP 1.1 version/scope contract integrity PASS; release remains NO-GO")
