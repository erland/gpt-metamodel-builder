# Sparx EA adapter

Sparx EA är en plattformsadapter. Canonical YAML i `metamodel/` är sanningskälla.

## Adapterdelar

- `mapping.yaml` – MDG-/profilmetadata, metaclasses och filmanifest.
- `stereotypes.yaml` – canonical element/relation → Sparx stereotype + UML metaclass.
- `tagged-values.yaml` – canonical properties → Tagged Values.
- `diagrams.yaml` – canonical viewpoints → diagramprofiler.
- `toolboxes.yaml` – toolboxprofiler och sidor.
- `quick-linker.yaml` – tillåtna/snabba kopplingar härledda från canonical relationer.
- `shapescripts.yaml` + `shapescripts/` – presentation som är Sparx-specifik.

Referensimplementation finns i `examples/architecture-lite/platforms/sparx-ea/`.

En generator får endast läsa canonical modellen och denna adapter. Genererad MDG XML får aldrig bli canonical source.
