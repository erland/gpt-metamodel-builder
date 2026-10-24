# Conformance and scope

Format version: `1.0.0`.

## Required consumer behaviors
- Parse MMP ZIP and directory packages without executing content.
- Validate inventory, hashes, identity and seven mandatory entrypoints.
- Resolve all canonical JSON Schema references without network access.
- Report unsupported constraints rather than silently treating them as passed.
- Reject unsafe ZIP paths, duplicate members, missing files and tampered bytes.

## Conformance example
`examples/architecture-example.mmp.zip` is expected to be accepted by a conforming read-only consumer.

## Current limitations
The reference consumer validates a substantial but incomplete semantic subset. The specification is currently a project-defined contract. No external implementation or independent certification is claimed. Advanced OCL/expression constraints need separately defined evaluation profiles.


## Machine-readable baseline test suite

`conformance/test-manifest.json` lists each case, `expected: accept|reject`, test package path, and SHA-256. `conformance/run_suite.py` compares independent consumer exit codes with expectations. Cases include valid baseline, bad SHA, duplicate ID, unknown parent, inheritance cycle, unknown relationship endpoint, required-field omission, unsupported format major and an undeclared ZIP member.

This suite is a **baseline subset** of Core behavior. It does not yet establish complete cardinality, property inheritance, constraints, notation, viewpoint or version-evolution conformance. A passing result is not a full MMP Core certification.
