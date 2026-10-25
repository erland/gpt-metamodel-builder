# CORE-007 – fullständig instansgraf för elementändpunkter (kandidat)

Status: **PARTIAL / NO-GO**. Denna etapp introducerar en fristående, frivillig grafadapter, inte ett nytt MMP-paketformat eller generell instansvalidator.

## Indata

```yaml
complete: true
instances:
  - {id: a1, type: application}
  - {id: b1, type: process}
edges:
  - {id: e1, relationship: serves, source: a1, target: b1}
```

`complete: true` är ett **uttryckligt påstående från anroparen** om att hela populationen av elementinstanser och relationsförekomster för aktuell prövning finns med. Verktyget kan inte själv bevisa att externa data är fullständiga; utan flaggan avvisas grafen.

`validate_graph` kontrollerar unik instans- och relationsförekomstidentitet, kända element- och relationstyper, existerande ändpunktsreferenser samt att instansernas typer ligger inom de deklarerade käll- och måltypmängderna. Den här etappen stöder endast *direkta* elementtypsreferenser. Inget implicit arv, inga `allowed_type_pairs` och inga typade relations-/junction-ändpunkter antas vara instansvaliderade av denna adapter. Junctions eller `typed_refs` avvisas med `not_supported`.

För alla deklarerade instanser vars typ är tillåten på en relationsändpunkt räknas antal förekomster för respektive relationstyp och `source`/`target` **var för sig**. Även noll förekomster ingår. Resultatet skickas till den tidigare strikta `validate_incidence`-analysen. Saknas cardinality på en ändpunkt som faktiskt prövas rapporteras `not_supported` i stället för att anta en gräns.

## Bakåtkompatibilitet

Canonical YAML och MMP 1.0 ändras inte. Detta är en opt-in-funktion som inte skriver till originalmodeller och inte migrerar äldre instansformat. Befintliga `source.types`/`target.types` behåller sin betydelse.

## Nästa steg och begränsningar

En framtida utökning ska införa ett versionssatt instansgrafskontrakt med explicit typade ändpunkter, junction-topologi, relation-till-relation-förekomster, arv och koppling till typade pairwise-begränsningar. Fram till dess utgör detta inte bevis för full CORE-007, CORE-015/016 eller ArchiMate-konformitet.
