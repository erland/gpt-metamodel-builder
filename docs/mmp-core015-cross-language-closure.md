# CORE-015 – Normaliserade relationspar i Python och TypeScript

Denna etapp kopplar in transitiv expansion av **elementtypsarv** i båda fristående MMP-konsumenterna. Utdatafältet `effective_pairs` är en sorterad, dubblettfri mappning från relations-ID till tillåtna par av **konkreta** elementtyper. Det finns bara för relationer som explicit deklarerar `allowed_type_pairs`; övriga får **ingen** implicit kartesisk produkt.

## Bakåtkompatibilitet och migration

- Gammal canonical YAML och MMP 1.0 utan `allowed_type_pairs` ger tom `effective_pairs` och kräver ingen migrering.
- Paket med explicita par exporteras bara i MMP 1.1-kandidat med obligatorisk pairwise-profil, enligt tidigare beslut.
- Ingen import skriver om original-YAML; utdata är en **beräkning**, inte ett nytt lagrat canonical fält.
- Inga par härleds automatiskt från gamla `source.types` och `target.types`.

## Verifiering

`scripts/test_mmp_effective_pairs_package.py` skapar ett verkligt kandidatpaket med baskälla, basmål och undertyper, jämför normaliserat resultat och verifierar att legacy-paket inte får syntetiska regler. GitHub Actions bygger TypeScript-konsumenten och kör samma paket mot båda implementationerna och jämför resultaten exakt.

## Begränsning

**CORE-015 är fortsatt PARTIAL.** Koden beräknar transitivt **elementtypsarv**, men inte arv mellan relationstyper, specialiseringens begränsningar vid flera föräldrar, CORE-016 relationer/junctions som ändpunkter eller full instansvalidering. MMP 1.1 är fortsatt NO-GO tills dessa semantiker är definierade och testade.
