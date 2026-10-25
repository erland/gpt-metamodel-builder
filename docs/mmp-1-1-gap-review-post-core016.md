# MMP 1.1 – gap- och releasegranskning efter PR #65

**Beslut: NO-GO för publicering av MMP 1.1.0 som fullständig specifikation.**

Datum: 2026-10-25. Underlag: implementationen och testregistreringen på `main` efter PR #65, tidigare readiness-matris `conformance/mmp-1-1-readiness.json`, tidigare beslut och det integrerade scenariot `scripts/test_mmp_core015_core016_integration.py`.

Detta är en **käll- och kodspårbar granskning, inte ett nytt körningsprotokoll**. Den skiljer mellan *implementerad kod*, *testfall registrerade i CI*, *tidigare verifierade delmängder* och *fortfarande obekräftad konformitet*. Befintlig publicerad MMP 1.0.0 förändras inte.

## Vad som finns efter PR #65

| Område | Status | Spårbart underlag | Avgränsning |
| --- | --- | --- | --- |
| CORE-013: paketbunden förhandling av obligatoriska profiler | Implementerad kandidatdelmängd | `scripts/export_mmp.py`, `scripts/import_mmp.py`, `scripts/test_mmp_core013_candidate.py` | Inte ett slutligt externt certifierat profilkontrakt |
| CORE-015: explicita elementbaserade par | Implementerad kandidatdelmängd | `schemas/metamodel.schema.json`, `scripts/mmp_effective_pairs.py`, `scripts/test_mmp_effective_pairs_package.py` | Full instanskonformitet och modelldiff saknas |
| CORE-015: relationstypsarv och multipla föräldrar | Implementerad kandidatdelmängd | `scripts/test_mmp_pair_inheritance.py`, `scripts/test_mmp_relation_inheritance_package.py` | Vald restriktiv snittpolicy behöver normativt fastställande och externa konsumentprov |
| CORE-016: typade ändpunkter/junctions | Implementerad kandidatdelmängd | `scripts/test_mmp_typed_endpoints_package.py` | Referensintegritet och roundtrip, inte instans-/topologisemantik |
| CORE-016: exakta typade par | Implementerad kandidatdelmängd | `scripts/test_mmp_typed_pair_package.py` | Deklarativ kontroll; ärvda typade par och junction-instansvalidering saknas |
| Integrerat paketflöde | Test tillagt | `scripts/test_mmp_core015_core016_integration.py`, TypeScript-workflow | Syntetiskt ArchiMate-inspirerat scenario, inte full ArchiMate-verifiering |
| MMP 1.0 bakåtkompatibilitet | Skyddat i testade delmängder | negativa exporter, `scripts/test_mmp_export.py`, `scripts/test_mmp_import.py` | Ingen generell garanti för alla externa konsumenter |

## Prioriterade hinder inför release

### P0 – måste lösas före GO

1. **CORE-007: normativa endpoint-/instanskardinaliteter.** Dokumentera roller, multiplicitet, relationstypsspecialisering och hur faktiska modellinstanser valideras. Nuvarande tester är huvudsakligen deklarativa.
2. **CORE-016: junction- och relation-till-relation-semantik.** Definiera instanstyper, riktning, topologi, eventuella cykler och felbeteenden; bind dem till gemensamma positiva/negativa fullpaket-fixtures.
3. **CORE-015/016: arv för typade par.** Förklara hur `allowed_typed_pairs` och relationstypsarv kombineras, hur multipla föräldrar snävar in domänen och vad som ska avvisas, utan implicit kartesisk produkt.
4. **CORE-009/011: grundsemantik för required/kardinalitet och kanoniska värden.** Fatta versionsbundet policybeslut och verifiera numeriska gränser/precision, tidszoner och URI-jämförelser i båda konsumenterna.
5. **Normativ konformitetsmatris.** Uppdatera kravstatus baserat på exekverbara, jämförbara referensresultat, verifierade fullpakettester och en tydlig definition av `supported`, `partial` och `not_supported`. Nuvarande äldre readiness JSON visar felaktigt CORE-013 som utan on-wire-kontrakt; skriv inte om dess historiska källbedömning utan spårbar ny version.

### P1 – releaseavgränsningar som måste beslutas

6. **CORE-012 rules:** Antingen formellt utanför Core (uttalat `not_supported`) eller separat körbar och testad profil; YAML-läsning är inte exekvering.
7. **ArchiMate 3.2-fixture med versionslåst källmaterial:** Verifiera konceptinventering och exakt relationsmatris; gör automatisk roundtrip och rapportera bortfall. Tidigare arbetsuppgifter om 62 koncept/3 841 par är inte här verifierade som releasefakta.
8. **Extern interoperabilitet:** Minst en oberoende paketkonsument utanför detta repo, och manuell Sparx EA-gate endast där MDG faktiskt ska stödjas. Två interna referenskonsumenter är viktiga men inte externa bevis.
9. **Modelldiff/migration:** Flagga försnävning av pairwise-mängder, endpointtyp och känd instanspåverkan som breaking eller needs_review. Äldre YAML ändras aldrig implicit.

## Föreslagen arbetsordning

- **PR #67 (förslag):** CORE-007 strikt kandidatprofil för instanskardinalitet inklusive delade positiva/negativa fixtures, utan MMP 1.0-förändring.
- Nästa: CORE-016 normerad junction-/relationsinstansmodell och typed-pair-arv.
- Därefter: CORE-009/011 policybeslut och testvektorer; uppdaterad spårbar readiness-matris och fullskalig ArchiMate-fixture.
- Sist: oberoende interoperabilitet, migreringsgranskning och release-GO/NO-GO.

## Migrationsprincip

Gammal canonical YAML och publicerad MMP 1.0.0 behåller sin betydelse. Nya kritiska krav får endast införas via uttryckligt paketspecifikt versions-/profilkontrakt med fail-closed import. Konvertering av legacy-ändpunkter till exakta par eller typade ändpunkter får bara ske som opt-in på kopia, med synlig konsekvensrapport och utan att fabricera relationstrippelkombinationer.

## Beslutsregel

**GO för MMP 1.1.0 först när:** varje obligatoriskt Core-krav har normativt definierad semantik, körbara delade språkoberoende testfall, verifierad Python/TypeScript-paketparitet, negativa säkerhets-/kompatibilitetsfall samt minst ett oberoende konsumentbevis enligt releaseomfattningen. Tills dess ska formatet märkas **candidate/partial**, och varken **1.1.0 stable** eller **full ArchiMate-compatible** deklareras.
