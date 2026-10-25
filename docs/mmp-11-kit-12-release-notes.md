# Specification Kit 1.2.0 — release candidate notes

**Release status: candidate / NO-GO, not published.**

- Kit version: **1.2.0** (new, separate distribution).
- Target MMP package format: **1.1.0**, limited declared-profile scope.
- Earlier Kit **1.1.0**: package format **1.0.0**, unchanged.
- Required capabilities: pairwise relationships, typed endpoints, exact typed pairs, junction-structure metadata, and required/default-presence where declared. Unsupported required capability versions fail closed.
- Evidence: shared Python and TypeScript conformance suites, a combined multi-profile actual-package test, and reproducible ZIP + SHA-256 inventory checks.
- Not guaranteed: complete instance-graph validation, full Core 1.1, behavioral junction rules, relation derivation, rule evaluation, or external certification.

**Important:** Historic MMP 1.0 specification documents remain included as an explicitly labeled baseline. Only the 1.1 limited-scope contract describes new candidate guarantees. Distribution from a release tag, final artifact verification and release authorization still remain.

Build: `python scripts/build_mmp_specification_1_2.py`. Check: `python scripts/test_mmp_specification_1_2.py`.
