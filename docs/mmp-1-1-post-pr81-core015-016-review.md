# MMP 1.1 – samlad CORE-015/016-konformitetsgranskning efter PR #81

**Beslut: PARTIAL / NO-GO för stabil MMP 1.1.0.** Datum: 2026-10-25. Underlag: mergad implementation efter PR #81, källkod, registrerade CI-test och historiskt granskningsunderlag. Bedömningen är inte en extern konformitetscertifiering.

## Förändring sedan tidigare granskning

| Krav | Bedömning | Tillagd konkret evidens | Avgränsning |
| --- | --- | --- | --- |
| CORE-015 | Kandidatdelmängd | Explicita elementpar, relationstypsarv och restriktiv snittpolicy, integrerade pakettester | Normativ samverkan mellan arv, subtyper och konkreta instanser inte fullständig |
| CORE-016 | Kandidatdelmängd | Typade ändpunkter, junctions, exakta typade par, restriktivt multipelt arv; Python och TypeScript prövar verkliga instanskanter | Inga generella AND/OR-flödes- eller aktiveringsregler |
| CORE-015/016 paketkedja | Avgränsat testad kandidat | PR #81: MMP 1.1-export, import, byteidentisk canonical roundtrip, paketkonsumenter och jämförbara instansgrafstester | Testet använder en avgränsad typad delmodell, inte alla äldre relationstyper eller externa konsumenter |

**Viktigt:** MMP-konsumenterna avvisar otillåtna format-/profilkontrakt; de kör inte generellt alla tänkbara instansgrafer. PR #81 ger därmed verifiering av ett faktiskt kandidatpaket och dess testsituation, inte ett generellt bevis på instanssemantik.

## Beslut som fortfarande blockerar GO

1. **CORE-007:** normativ instanspopulation, kardinalitet vid arv/specialisering och cykelpolicy.
2. **CORE-009/011:** required-/kardinalitetsregler och kanonisering av numeriska, datum-/tids-, URI- och andra värden i båda konsumenterna.
3. **CORE-012:** definiera som explicit ej stött i Core eller fristående regelspråksprofil.
4. **CORE-016:** junction AND/OR-beteende och betydelsen av operatorprofilen behöver normativt avgränsas; nu enbart struktur.
5. **Interoperabilitet och release:** versionslåsta normativa konformitetsfall och faktisk extern oberoende konsument.

## Rekommenderad prioritet

Efter denna granskning rekommenderas **CORE-009/011, värdekanonisering och required-semantik**, som nästa konkreta arbetsområde. Börja med normativa, språkneutrala testvektorer och explicit scope, utan att ändra befintlig MMP 1.0. Beslut om typernas format och jämförelseregler bör föregå ny exekverbar funktionalitet.

Maskinläsbar spårbar bedömning: `conformance/mmp-1-1-post-pr81-core015-016.json`. Tidigare granskningsfiler har inte ändrats.
