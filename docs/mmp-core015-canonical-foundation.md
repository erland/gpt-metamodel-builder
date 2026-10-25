# CORE-015 etapp 1 – canonical pairwise-relationer

Status: **canonical foundation only**, inte full MMP 1.1-stöd.

## Tillagt
`relationships[].allowed_type_pairs` är ett **valfritt** fält med exakta `{source,target}`-par av elementtyper. Fältet är förberett för CORE-015 men ändrar inte betydelsen av äldre `source.types`/`target.types`.

- JSON Schema kräver 1+ par med två referenser och förbjuder extra nycklar.
- Semantisk validator avvisar okända elementtyper, par utanför deklarerade ändpunktsmängder och dubbletter.
- `export_mmp.py` stoppar uttryckligen export om någon relation deklarerar `allowed_type_pairs` i stället för att låta en äldre konsument felaktigt acceptera den med en kartesisk produkt.
- CI-smoke kontrollerar positiva, negativa och oförändrade legacy-modeller.

## Migrering och bakåtkompatibilitet

Gammal `schema_version: 1` och gamla modeller utan fältet förblir giltiga, utan omskrivning. Ingen automatisk härledning från gamla `source.types` × `target.types` eftersom det skulle kunna introducera falskt tillåtna kombinationer. Framtida migration måste vara explicit, köras på en kopia och redovisa semantiska luckor.

För exakta par som refererar till **abstrakta supertyper** och ärvda relationer återstår explicit expansions-/konfliktpolicy i nästa etapp. Denna första etapp tillåter endast par inom de direkt deklarerade endpoint-mängderna; ingen automatisk effektivering eller härledning sker.

## Återstående gate

Full CORE-015 kräver förstaklassig konsumenttolkning i MMP 1.1-kandidat, Python/TypeScript-fullpaketparitet, normaliserad regelmängd, migrations- och roundtrip-test samt CORE-016 typade relationer/junctions. Kandidaten är inte releaseklar.
