# MMP Specification & Developer Kit v1.1.0

Specification Kit version **1.1.0**, carrying MMP **package format 1.0.0** (these versions are intentionally independent). Metadata: `specification-kit.json`.\n\nAn independent, tool-neutral specification kit for **Metamodel Exchange Package (MMP)**. This is a project-defined format, **not an external standard**. This kit contains the normative format contract and machine-readable JSON Schemas, a sample package, a reference consumer, and conformance guidance.

Start with `specification/mmp-v1.md`, then `specification/implementation-guide.md`. The sample is `examples/architecture-example.mmp.zip`.

The reference consumer is informative and requires Python 3, PyYAML, jsonschema and referencing:

```bash
python reference-implementation/mmp_v1_consumer.py examples/architecture-example.mmp.zip
```

`SHA256SUMS.txt` checks all packaged files except itself. This kit is **not** a concrete MMP file and is **not** Metamodel Builder's executable Engine.


## Portable conformance suite

The kit includes `conformance/test-manifest.json`, nine generated `conformance/packages/*.mmp.zip` fixtures, and `conformance/run_suite.py`. Run the reference consumer from the extracted kit:

```bash
python conformance/run_suite.py --kit mmp-specification-kit-1.1.0.zip --consumer reference-implementation/mmp_v1_consumer.py
```

A different consumer executable can be supplied with `--consumer` if it accepts one package path and returns zero only when accepted. Cases exercise a **subset** of MMP 1.0.0 structural/security/semantic invariants; passing does not certify full proposed Core 1.1 profile support.

## Final release acceptance

See `specification/release-acceptance.md` for the testable scope of the reproducible Specification Kit 1.1.0 (MMP format 1.0.0). The release gate checks all SHA-256 inventory entries and packaged fixtures and preserves an explicit **NO-GO** for full MMP 1.1 Core conformance.
