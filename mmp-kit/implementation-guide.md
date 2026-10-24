# Independent consumer implementation guide

1. Open ZIP safely, rejecting duplicate names, path traversal, symlinks and oversized members.
2. Parse `manifest.yaml` with a non-executable YAML parser; validate against `schemas/mmp-manifest-v1.schema.json`.
3. Validate complete manifest file inventory and SHA-256 before parsing canonical data.
4. Resolve seven required `entrypoints`; `guidance` is optional.
5. Validate canonical files with their included offline JSON Schemas. Resolve references exclusively from local schemas.
6. Check global identity: `namespace#percent-encoded-local-id`; never use the displayed label as identity.
7. Check cross-file semantics and explicitly report unsupported rule languages as `not_supported`. No MMP source text is executable.
8. Keep format compatibility separate from the producer application version.

A consumer can use any programming language. The packaged Python reference consumer is **informative**, not a normative dependency.
