#!/usr/bin/env python3
"""Contract-only checks. Export/import behavior is covered by later PRs."""
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker

ROOT=Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/"schemas/mmp-manifest-v1.schema.json").read_text())
Draft202012Validator.check_schema(schema)
validator=Draft202012Validator(schema,format_checker=FormatChecker())

def example():
    entries={k:f"canonical/{k}.yaml" for k in
        ("metamodel","properties","constraints","viewpoints","notation","provenance","version")}
    files=[{"path":p,"role":"canonical","media_type":"application/yaml","sha256":"a"*64} for p in entries.values()]
    files += [{"path":f"schemas/{k}.schema.json","role":"schema","media_type":"application/schema+json","sha256":"b"*64}
        for k in (*entries.keys(),"common-definitions")]
    return {"package_format":"mmp","package_format_version":"1.0.0",
            "metamodel":{"id":"example","name":"Example","version":"1.0.0","namespace":"https://example.org/mm"},
            "producer":{"name":"Metamodel Builder","version":"1.2.2"},
            "generated_at":"2026-10-24T12:00:00Z","entrypoints":entries,"files":files}

good=example()
assert not list(validator.iter_errors(good))
for mutate in [
    lambda d:d["metamodel"].pop("namespace"),
    lambda d:d["entrypoints"].pop("version"),
    lambda d:d["files"][0].update(path="../escape"),
    lambda d:d["files"][0].update(sha256="not-a-hash"),
    lambda d:d.update(package_format_version="2.0.0"),
]:
    import copy
    bad=copy.deepcopy(good); mutate(bad)
    assert list(validator.iter_errors(bad)),bad
print("MMP manifest schema PASS: valid manifest and five negative contract cases")
