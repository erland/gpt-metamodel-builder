#!/usr/bin/env python3
"""Guard version promises and compatibility status before release."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
decision=json.loads((root/"conformance/mmp-version-decision-v1.json").read_text())
strict=json.loads((root/"conformance/strict-core-coverage-v1.json").read_text())
readiness=json.loads((root/"conformance/mmp-1-1-readiness.json").read_text())
assert decision["decision_version"]=="1.0.0"
assert decision["stable_format"]=="1.0.0"
assert decision["next_format_version"]=="deferred"
assert decision["full_core_1_1"]=="not_verified"
assert decision["release_gate"]=="NO-GO for MMP 1.1.0"
assert strict["overall"]=="partial" and strict["release_decision"]=="NO-GO"
assert readiness["overall"]=="not_ready"
assert len(decision["rules"])==6
assert {x["id"] for x in decision["rules"]}=={f"FMT-{n:03d}" for n in range(1,7)}
assert {"stable","opt_in","deferred"}=={x["classification"] for x in decision["rules"]}
assert "strict-core-candidate" in decision["optional_profiles"]
for name in ["docs/mmp-v1-contract.md","docs/mmp-version-compatibility-decision.md"]:
    assert (root/name).is_file()
print("PASS: MMP 1.0.0 release scope frozen; MMP 1.1.0 remains NO-GO")
