# MMP required + cardinality – explicit policy decision

Status: **proposed opt-in Core profile** for future MMP 1.1, not published MMP 1.0.0 semantics.

**Decision proposal:** `required: true` means an effective minimum of one value, even when cardinality declares a zero minimum. The effective lower bound is `max(declared_min, required ? 1 : 0)`; the upper bound comes unchanged from cardinality, or is unbounded when omitted. If effective minimum exceeds an explicit maximum (e.g. `required: true, cardinality: "0"`), mark **invalid** in this opt-in profile. `required: false` does not weaken an explicit positive cardinality minimum.

A missing cardinality implies no specific upper bound; this rule does **not** impose max=1. Default-value fulfillment is *not* decided here: presence can be satisfied by a normatively valid default only after separate default policy approval.

**Compatibility:** The pre-existing MMP 1.0.0 helpers and import/export remain untouched; the older `required_profile` continues to report zero-minimum conflicts as `undecided`. Only new `required_minimum_policy` is evaluated in the opt-in test suite, so existing 1.0.0 files are not newly rejected. Normalizing conflicts during export or mandating this interpretation for all consumers would require a separate versioning decision.

Nine shared vectors in `interop/required-policy-v1.json` test the decision in Python and TypeScript.
