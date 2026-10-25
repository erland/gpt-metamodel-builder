# CORE-016 – Exakta typade relationspar (canonical kontrakt)

Status: **etapp 1, PARTIAL**, MMP 1.1 är fortsatt **NO-GO**.

## Förslag och representation
`relationships[].allowed_typed_pairs` är valfritt och består av exakta `source` och `target` med `{kind,id}`, där `kind` är `element`, `relationship` eller `junction`. Alla referenser ska finnas i respektive ändpunkts `typed_refs` och existera i rätt namnrymd. Dubbletter är inte tillåtna. En relation kan inte blanda `allowed_typed_pairs` och äldre `allowed_type_pairs`, eftersom konfliktprioritet ännu saknar normerad semantik.

```yaml
junctions:
  - id: and_junction
    name: AND
relationships:
  - id: connection
    name: Connection
    source:
      types: []
      typed_refs:
        - kind: junction
          id: and_junction
    target:
      types: []
      typed_refs:
        - kind: relationship
          id: connection
    allowed_typed_pairs:
      - source: {kind: junction, id: and_junction}
        target: {kind: relationship, id: connection}
```

## Kompatibilitet och migrering
Modeller utan det nya fältet fortsätter utan omskrivning. Befintliga elementbaserade `allowed_type_pairs` fortsätter att vara giltiga. Inga exakta par härleds från gamla endpoint-mängder. Eftersom ingen MMP-konsument ännu tolkar typade par får de inte exporteras ens med `--candidate-1-1`. Export spärras före paketskrivning i stället för att tyst tappa semantik. Framtida migration ska ske opt-in på kopia av originalet.

## Kvarstående
Nästa steg är en explicit kapabilitet, full konsumenttolkning i Python och TypeScript, tester av paketparitet och tydlig policy för ärvda relationstyper och instanser/junction-topologi. Typade par behandlas tills dess som **deklarativa exakta referenser**, inte som en färdig härledningsalgoritm.
