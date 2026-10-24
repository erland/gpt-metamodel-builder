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

## Semantic interoperability golden vector

`conformance/effective-properties-v1.json` defines multiple inheritance (including diamond inheritance), repeated inherited property-set and property IDs, and distinct property IDs sharing the same display name. Both Python and TypeScript consumers calculate sorted effective set/property IDs and compare against the independently declared expected JSON. This verifies a semantic Core subset; it is **not** full 1.1 profile certification.

## Cardinality vectors

`conformance/cardinality-v1.json` exercises interval parsing and explicit undecided `required` conflicts in Python and TypeScript. This is opt-in analysis, **not** additional rejection by an MMP 1.0.0 consumer.

## Default value vectors

`conformance/default-values-v1.json` contains datatype, enumeration, and cardinality-sensitive default value cases. Python and TypeScript implementations run the same cases without changing MMP 1.0.0 admission semantics. This subset does not establish full Core conformance.

## Relationship semantics vectors

`conformance/relationship-semantics-v1.json` tests subtype-compatible endpoint roles, direction and navigability across Python and TypeScript. Relationship-type endpoint inheritance narrowing remains unspecified; this is a partial Core test profile only.
