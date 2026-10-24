# MMP 1.1 – samlad readiness-granskning

Status: **NO-GO för release av MMP 1.1.0**. Granskning av tillgängliga artefakter från PR #27–36, inte en ny normativ specifikation. Publicerad MMP 1.0.0, dess scheman och import-/exportpolicy ändras inte i denna PR.

## Verifierad bas

De två fristående referenskonsumenterna är `interop/mmp_v1_consumer.py` och `interop/typescript/src/consumer.ts`. CI använder dels nio gemensamma MMP 1.0.0-paket för accept/reject, dels språkneutrala JSON-testvektorer för utvalda semantiska funktioner. Dessa två kategorier får **inte** blandas ihop: en godkänd testvektor för en fristående hjälpfunktion innebär inte att hela paketimporten tillämpar regeln, och en CI-grön PR är inte bevis för full konformitet med ett ännu opublicerat Core 1.1-kontrakt.

Maskinläsbar spårbarhetsmatris: `conformance/mmp-1-1-readiness.json`. Den skiljer `covered_subset`, `open` och `decision_required` och refererar till faktiska källfiler och tester.

## Vad vi faktiskt har täckt

| Område | Befintligt verifierbart underlag | Bedömning |
| --- | --- | --- |
| Paketsäkerhet, manifest, SHA-256 och grundläggande semantik | `scripts/mmp_conformance_fixtures.py`, Python- och TypeScript-baslinjen | Delmängd verifierad |
| Identitet och arv | `scripts/test_mmp_identity_evolution.py`, `interop/effective-properties-v1.json` | Delmängd verifierad |
| Egenskapsgrupper, diamantarv och ID-baserad deduplicering | `interop/effective-properties-v1.json` | Delmängd verifierad |
| Kardinalitetsuttryck | `interop/cardinality-v1.json` | Kandidatsemantik testad separat |
| Datatyper och standardvärden | `interop/default-values-v1.json` | Kandidatsemantik testad separat |
| Relationsroller, navigerbarhet och undertyper | `interop/relationship-semantics-v1.json` | Kandidatsemantik testad separat |
| Modellversioner och extensions | `interop/version-extension-v1.json` | Konservativ delmängd, inte hel modellkompatibilitet |

## Slutliga frågor före 1.1.0

1. **CORE-007:** Definiera rollbaserad endpoint-kardinalitet och test av relationers antal på instansnivå, samt bestäm hur ändpunktsbegränsningar får förändras vid relationstypsarv.
2. **CORE-009:** Fatta explicit kompatibilitetsbeslut om `required: true` + `cardinality: 0..*`. Tvinga inte in ett val i äldre 1.0.0-konsumenter.
3. **CORE-011:** Bestäm intervall för heltal, decimalprecision, datum/tidszon och URI-jämförelse. Implementera därefter samma kanoniska testresultat i båda språken.
4. **CORE-013:** Separera frivilliga extensions från kritiska profiler med explicit versions-/stödförhandling. Dagens `extensions` saknar sådant fält.
5. **CORE-012:** Definiera en faktiskt körbar Rules-profil, eller bekräfta att Core inte gör anspråk på regelutvärdering. Bevara `not_supported` i frånvaro av utvärderare.
6. **Konformitetsbevis:** Utöka tester för vardera obligatorisk regel med positiva/negativa paket och semantiska golden-resultat. Konsumentdeklarationer ska vara kopplade till körd testsvit, inklusive ej stödda funktioner.

## Konformitetsprofiler

**Föreslagen obligatorisk profil:** `mmp-core`. Full `supported` ska inte deklareras förrän alla dess normativa kriterier är testbara och verifierade.

**Föreslagna valfria profiler:** `mmp-rules`, `mmp-notation`, `mmp-viewpoints`. Dessa har för närvarande ingen verifierad full konformitet och ska därför inte förväxlas med tillgänglig YAML-inläsning.

Den maskinläsbara deklarationen i `schemas/mmp-conformance-declaration-v1.schema.json` visar en kapabilitet, inte ett oberoende intyg. `partial` och `unsupported` är korrekta där funktioner inte har prövats.

## Beslut och rekommenderad fortsättning

**NO-GO** för att publicera `package_format_version: 1.1.0` nu. Nästa PR bör åtgärda ett begränsat blockerande område, först CORE-007 (relationstypsarv och endpoint-kardinalitet), följt av CORE-009 och värdenas kanonisering. Därefter utökad gemensam konformitetssvit, med 1.0.0-regression bibehållen.

Ingen omtolkning av tidigare schema-giltiga paket bör smygas in i 1.0.0. Om ett nytt obligatoriskt kontrakt avvisar tidigare paket ska vi välja uttrycklig opt-in-strikt profil eller ompröva behov av major-version.
