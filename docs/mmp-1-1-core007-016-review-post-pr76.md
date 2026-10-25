# MMP 1.1 – CORE-007/016 sammanhållen granskning efter PR #76

**Beslut: NO-GO för MMP 1.1.0 stable.** Granskningsdatum 2026-10-25. Underlag: källkod, delade testvektorer, registrerade CI-steg och tidigare granskning i `conformance/mmp-1-1-post-core016-review.json`. Detta är **inte** oberoende certifiering; ny exekvering av hela konformitetssviten redovisas separat av CI.

## Bedömning

| Område | Status | Styrkta kandidatfunktioner | Fortsatt blockerande |
| --- | --- | --- | --- |
| CORE-007 | **Kandidatdelmängd** | Explicit komplett instanspopulation; förekomsträkning inklusive noll; kardinalitetsprövning för element-, relations- och junction-ändpunkter; konservativ avvisning av cykliska relationsinstansreferenser | `complete: true` är datakällans påstående; arv/specialisering och full normativ kardinalitetssemantik saknas; cykelpolicy är provisorisk |
| CORE-016 | **Kandidatdelmängd** | Typade ändpunkter, exakta deklarerade par, junction-instanser, separat förhandlad operatorprofil och paketbaserad strukturell validering i Python/TypeScript | AND/OR-flöde och aktivering odefinierade; anslutningsregeln är endast kandidat; ärvda typade par och full junction-cykelsemantik saknas |

Båda områdena har negativa testfall för ogiltiga och saknade deklarationer. Python och TypeScript använder gemensamma testdata för typade instansgrafer och jämförbar paketbunden junction-struktur. Detta verifierar *testade delmängder*, inte att två implementationer oberoende stödjer all semantik.

## Statusnivåer

- **Testad kandidatdelmängd:** konkret implementation och registrerade tester, med dokumenterade avgränsningar.
- **Beslut krävs:** normativtolkning, versionsprofil eller jämförbar exekverbar acceptans saknas.
- **Inte stödd:** beteendesemantik eller instansfall som avvisas `not_supported`.
- **Full konformitet:** används inte för något av dessa områden före versionslåsta normativa krav och extern verifiering.

## Kvarvarande MMP 1.1-blockerare

1. CORE-015/016: definiera och testa **ärvda typade par** med multipelt relationstypsarv och strikt fail-closed avvisning av tvetydiga fall.
2. CORE-007: fastställ kardinalitetens räknedomän, subtypeffekt och relation-till-relation-cykelsemantik normativt.
3. CORE-016: fastställ om AND/OR-beteende ska vara en separat profil, med exakt semantik eller dokumenterat `not_supported`.
4. CORE-009/011: erforderlighet, numerisk precision, datum/tidszoner och kanoniska värden.
5. CORE-012: separat regelspråksprofil eller uttryckligt utanför Core.
6. Komplett versionslåst ArchiMate-fixture, objektiv konformitetsmatris och extern oberoende interoperabilitet.

## Kompatibilitet och nästa steg

Den historiska granskningsfilen ändras inte. MMP 1.0 och canonical YAML lämnas oförändrade. Ingen automatisk migration görs. Maskinläsbar status och evidenskontroll finns i `conformance/mmp-1-1-core007-016-review-20261025.json` och `scripts/test_mmp_core007_016_review.py`.

**Rekommenderat nästa utvecklingssteg:** fastställ CORE-015/016:s effektiva ärvda typade par och bygg gemensamma positiva och negativa Python/TypeScript-fixtures samt kandidatpakettest. Detta undanröjer nästa centrala semantikblockerare utan att blanda in ArchiMate-specifik junction-aktivering i Core.
