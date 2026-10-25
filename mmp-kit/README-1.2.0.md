# MMP Specification Kit 1.2.0 — limited MMP 1.1 release

This kit describes **MMP package format 1.1.0** in a limited, explicitly negotiated capability-profile scope. It was first distributed in project release **v1.4.0**. The separate earlier Specification Kit 1.1.0 targets package format 1.0.0.

## Start here

Read `specification/mmp-1-1-limited-contract.md` for the scoped contract, `specification/release-notes-1.2.0.md` for limitations, and `conformance/release-status-1.2.0.json` for the recorded publication and verification evidence.

The bundled `specification/mmp-v1.md`, `specification/version-compatibility-decision.md`, and legacy fixtures describe the **1.0.0 baseline**. The included `conformance/mmp-1-1-limited-release-decision.json` and `conformance/mmp-1-1-version-scope.json` record **historical candidate decisions** and must not be interpreted as the current publication status.

## Supported limited scope

Package manifest and canonical required-capability declarations must agree. Unsupported mandatory capabilities are rejected. The tested import/export subset preserves declared types, exact typed relationship pairs, structural junction metadata, and required/default presence policy when its capability is declared.

## Exclusions

No claim of full Core 1.1 or comprehensive instance-graph validation, implicit subtype expansion, junction activation, relationship derivation, general rule evaluation, universal datatype/URI canonicalization, or external interoperability certification.

## Integrity

`SHA256SUMS.txt` covers every other kit member. The artifact verifier checks its contents, matching release SHA-256, reproducible source rebuild and conformance gates. Publishing a new artifact requires rerunning the release checks. Previously published v1.4.0 ZIPs are immutable historical artifacts and are not silently replaced.
