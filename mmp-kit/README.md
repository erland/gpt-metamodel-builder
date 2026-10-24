# MMP Specification & Developer Kit v1.0.0

An independent, tool-neutral specification kit for **Metamodel Exchange Package (MMP)**. This is a project-defined format, **not an external standard**. This kit contains the normative format contract and machine-readable JSON Schemas, a sample package, a reference consumer, and conformance guidance.

Start with `specification/mmp-v1.md`, then `specification/implementation-guide.md`. The sample is `examples/architecture-example.mmp.zip`.

The reference consumer is informative and requires Python 3, PyYAML, jsonschema and referencing:

```bash
python reference-implementation/mmp_v1_consumer.py examples/architecture-example.mmp.zip
```

`SHA256SUMS.txt` checks all packaged files except itself. This kit is **not** a concrete MMP file and is **not** Metamodel Builder's executable Engine.
