# Specification Kit 1.2.0 — release notes

**Publication history:** first published with project release **v1.4.0** (2026-10-25). The limited-profile scope is released; this does not imply full MMP Core 1.1 certification.

- Specification Kit: **1.2.0**; MMP package format: **1.1.0**.
- Legacy Kit **1.1.0** uses package format **1.0.0** and remains independently distributed.
- Supported capabilities are limited to declared pairwise relationships, typed endpoints, exact typed pairs, junction-structure metadata, and required/default presence where required.
- Unknown required capability versions fail closed.
- Verified with Python and TypeScript conformance tests, representative combined-profile package checks, reproducible builds and SHA-256 integrity.
- Excluded: full instance-graph validation, complete Core 1.1 certification, junction behavior, relationship derivation, general rule evaluation and independent external certification.

**Historical record:** older bundled candidate-stage decision files with `conditional_no_go` and open blockers describe a prior review. They are retained verbatim for traceability, not as the current publication decision. The current release-status record is `conformance/release-status-1.2.0.json`. Rebuilding this kit changes its checksum; do not silently replace an already published asset.

Build: `python scripts/build_mmp_specification_1_2.py`. Verify: `python scripts/test_mmp_specification_1_2.py`.
