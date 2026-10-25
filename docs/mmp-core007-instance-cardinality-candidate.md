# CORE-007 – opt-in instanskardinalitet (första kandidatprofil)

Status: **PARTIAL / NO-GO för full MMP 1.1-konformitet**.

Den nya, fristående funktionen `validate_incidence` kontrollerar uttryckligen angivna antal för en given trippel `(relationship type, endpoint role, instance)` mot relationsdefinitionens `source.cardinality` eller `target.cardinality`. Utvärderingen gäller alltså **ett deklarerat endpoint-instans-ID och en roll**, inte ett oklart globalt antal relationer. `source` och `target` räknas var för sig. Intervall kan vara `0`, `1`, `2..4`, `3..*` eller `*`, med inkluderande gränser. Ogiltiga intervall och negativa/icke-heltal avvisas.

## Avgränsning av indata och semantik

Indatat `counts` innehåller redan räknade förekomster. Anroparen ansvarar för fullständig inventering av instanser och förekomster. **Saknade poster tolkas aldrig som noll**, eftersom en sådan slutsats annars skulle göra ett ofullständigt underlag falskt giltigt. En relationsändpunkt utan deklarerad `cardinality` är `not_supported`, inte implicit `0..*`.

Detta är en separat opt-in-analysfunktion/testprofil; den ändrar inte MMP 1.0-inläsning, paketformatet, canonical YAML, eller existerande relationer. En full 1.1-profil behöver ännu definiera ett standardiserat instansformat, räkneregler vid junctions och relation-till-relation, transaktions-/rollsemantik, relationstypsarvets kardinalitetsbegränsning samt fullständighetskrav för verkliga instansgrafer.

## Verifiering och återstående krav

Gemensamma språkneutrala testvektorer i `interop/core007-instance-cardinality-v1.json` prövas separat av Python och TypeScript. Testsviten omfattar godkända antal, brott mot minimum/maximum, obegränsad övre gräns och odefinierad kardinalitet. Den provar **inte** faktisk uppräkning av kanter ur modellinstanser eller full MMP-kandidatpaketkonformitet.

**Nästa steg:** Introducera ett explicit, välavgränsat instansgrafkontrakt och beräkna förekomster från kanter; kontrollera fullständighet och typade ändpunkter med samma golden-fixtures innan den strikta CORE-007-profilen får deklareras som stödd i ett MMP-paket.
