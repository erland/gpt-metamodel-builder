# Sparx EA MDG validation and manual import fixture – v1

## Purpose
Step 6 adds deeper structural validation and an explicit manual Enterprise Architect import test. The deterministic validator is the automated gate; the EA import fixture is the product-level interoperability gate when Enterprise Architect is available.

## Shape Scripts
Sparx documents Shape Scripts as the `_image` special attribute on a profile stereotype. The generated `_image` value uses the `EAShapeScript 1.0` envelope and contains a Base64-encoded ZIP payload with `str.dat`. The generator stores the script as UTF-16 and fixes ZIP metadata so identical input produces byte-identical MDG output.

The automated validator decodes every `_image` payload and requires exact round-trip equality with its canonical adapter `.shape` source. It also performs a basic deterministic brace/string sanity check. This does not replace Enterprise Architect's own Shape Script parser.

## Structural MDG checks
The validator now checks:
- only expected top-level MDG sections are emitted;
- technology id/version;
- profile stereotype count and names;
- metaclass `AppliesTo` mappings;
- Shape Script payload and source equality;
- diagram count and toolbox reference integrity;
- toolbox page count;
- Tagged Values declared by the adapter;
- Quick Linker-equivalent `stereotypedrelationships`.

## Manual EA verification
Use `tests/sparx-ea/manual-import-fixture.yaml`. Run it against a disposable EA project and record the exact EA version/build. This fixture deliberately remains manual in v1 because the current project environment does not contain Enterprise Architect. A successful XML/schema validation is not represented as proof of successful EA import.
