# MMP Specification Kit 1.2.0 — limited MMP 1.1 candidate

This kit targets **MMP package format 1.1.0** with explicitly negotiated required capabilities. It is not the previous Specification Kit 1.1.0, whose package format is 1.0.0.

## Start here

Read `specification/mmp-1-1-limited-contract.md` for the candidate scope and `specification/release-notes-1.2.0.md` for the guarantees and exclusions. The bundled `specification/mmp-v1.md`, `specification/version-compatibility-decision.md`, and legacy conformance fixtures document the **1.0.0 baseline**, not a normative 1.1 replacement. Historic status records remain historic.

## Candidate guarantees

Package-level manifest and canonical required-capability declarations must match. Unsupported mandatory capabilities are rejected, not ignored. Declared element/relationship/junction structure, exact typed relationship pairs and declared profile metadata are preserved in the tested import/export subset. Required/default presence policy is active only when its versioned capability is required.

## Exclusions

No claim of full Core 1.1 or comprehensive instance validation, automatic subtype expansion, junction activation, relationship derivation, general rule evaluation, universal datatype/URI canonicalization, or external interoperability certification.

## Checks

`SHA256SUMS.txt` covers every other kit member. Use `python scripts/test_mmp_specification_1_2.py` in the repository to rebuild twice and compare byte-for-byte. Before release, run the combined-package gate and verify the **actual tagged artifact**. This kit is **candidate / NO-GO** until that final check.

The legacy kit is not overwritten.
