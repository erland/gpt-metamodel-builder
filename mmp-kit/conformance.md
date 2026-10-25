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

## Evolution and extension policy vectors

`conformance/version-extension-v1.json` tests a conservative type-ID change classifier and separately negotiated extension criticality across Python and TypeScript. This is *not* a complete package compatibility classifier; unrecognized extension semantics are not executed.

## MMP 1.1 readiness

The accompanying `conformance/mmp-1-1-readiness.json` and `specification/mmp-1-1-readiness-review.md` map CORE-001–014 to evidence and blockers. Their explicit conclusion is **NO-GO** for a new MMP 1.1.0 release; subset tests and reference implementations do not certify full Core 1.1 support.

## Proposed relationship inheritance semantics

`conformance/relationship-inheritance-v1.json` documents seven independently executed Python/TypeScript cases. This is opt-in proposed static type-specialization semantics, not MMP 1.0.0 admission and not full relationship-instance cardinality conformance.

## Proposed required-minimum policy

`conformance/required-policy-v1.json` verifies a versioned opt-in decision to interpret `required: true` as effective minimum 1. It is **not** a retroactive MMP 1.0.0 import rule; the former undecided helper is preserved.

## Candidate canonical text values

`conformance/canonical-values-v1.json` exercises text-level integer, decimal, date, UTC timestamp and restricted HTTP(S) URI canonicalization in both Python and TypeScript. This is a **limited opt-in proposal**, not full URI/number semantics and not MMP 1.0.0 import enforcement.

## Proposed extension negotiation

`conformance/extension-negotiation-v1.json` checks version-matched required and optional extensions across Python and TypeScript; this is a separate opt-in declaration, not 1.0.0 manifest semantics or trusted in-package authorization.

## Traced Core semantic subset suite

`conformance/core-semantic-suite-v1.json` maps independent Python/TypeScript helper golden-vector tests to CORE-001–014. The source-tree runner `scripts/run_mmp_core_semantic_suite.py --typescript --json-out report.json` produces a per-language, per-case and per-requirement machine-readable report. The kit contains a copy of the runner as reference; executing it requires the source tree and built TypeScript implementation. This remains a **subset helper suite** and explicitly states `full_core_conformance: not_verified`, even if all tests pass. Nine MMP 1.0.0 ZIP cases remain a separate acceptance baseline.

## Package-level semantic regression suite

`conformance/package-semantic-manifest.json` lists 4 additional hashed MMP ZIP cases verified by both Python and TypeScript through their ordinary read-only consumers. This tests a **subset** of semantic package behavior; future strict-profile requirements are not silently applied to legacy 1.0.0 packages.
