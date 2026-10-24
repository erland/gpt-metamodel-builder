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
