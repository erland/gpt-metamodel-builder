# CORE-007/016 – explicita junction-instanser och grundläggande topologi

Status: **PARTIAL / NO-GO** för MMP 1.1-konformitet.

Den frivilliga instansgrafsadaptern `validate_typed_graph` accepterar nu `junctions` som en explicit lista av instanser `{id, type}`. `type` måste finnas i metamodellens `junctions`-definitioner; alla instans-ID:n måste vara unika över element, relationer och junctions.

En relationsinstans kan använda `{kind: junction, id: j1}` som source eller target när dess relationsdefinition uttryckligen medger motsvarande `typed_refs`. Exakta `allowed_typed_pairs` kontrolleras för varje relation. Antal inkommande och utgående relationsförekomster räknas per relationstyp, roll och junction-instans, inklusive noll förekomster, via samma kardinalitetskontroll som element-/relationsinstanser.

```yaml
complete: true
instances:
  - {id: a1, type: actor}
junctions:
  - {id: j1, type: and_junction}
edges:
  - id: e1
    relationship: link
    source: {kind: element, id: a1}
    target: {kind: junction, id: j1}
```

## Begränsningar

Detta är **deklarativ kopplingstopologi**, inte full ArchiMate-junctionlogik. AND/OR-operation, flödesregler, förgrening/sammanslagning, topologiska cykler och transitive relationstypsspecialiseringar är ännu inte fastställda eller verifierade. `complete: true` är fortsatt ett påstående från datakällan.

Äldre canonical YAML och MMP 1.0 påverkas inte; ingen migrering eller omskrivning sker. Den äldre elementbaserade graffunktionen är oförändrad.

## Nästa steg

Fastställ normerad junction-beteendesemantik och policy för cykler, samt dela instansgrafsfixtures mellan Python/TypeScript innan någon fullständig `supported`-deklaration görs.
