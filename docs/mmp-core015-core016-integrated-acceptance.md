# Integrerat acceptanstest för CORE-015 och CORE-016

**Omfattning:** MMP 1.1-kandidat. Testet använder en **ArchiMate-inspirerad** syntetisk modell – det är inte ett bevis på överensstämmelse med hela ArchiMate 3.2 eller 4.0.

## Positiva scenarier

`scripts/test_mmp_core015_core016_integration.py` bygger en modell utifrån befintlig legacy-fixture och lägger till:

- Två föräldrarelationer och en specialiserad barnrelation utan egna exakta par; tillåtna kombinationer normaliseras restriktivt med snitt av föräldrarna (CORE-015).
- Transitiva elementtyper, med både baskälla/basmål och konkreta undertyper (CORE-015).
- En junction, en relation som ändpunkt samt en exakt `allowed_typed_pairs`-kombination mellan dem (CORE-016).
- Tre obligatoriska profiler i canonical och det integritetskontrollerade MMP 1.1-manifestet: `mmp-pairwise-relationships`, `mmp-typed-endpoints` och `mmp-typed-pairs`.

Testet kontrollerar kandidatpaketets export, importvalidering, canonical YAML som återställs byte-för-byte vid import till ny katalog, oförändrat original samt överensstämmelse för CORE-015:s `effective_pairs` med analysfunktionen. TypeScript-workflow jämför Python- och TypeScript-konsumenternas kompletta `effective_pairs`.

## Negativa scenarier

- Export av modellen till MMP 1.0 måste avvisas utan att något paket skapas.
- Var och en av de tre obligatoriska profilerna tas bort separat: kandidatexport måste avvisas utan paketskrivning.

## Bedömning av releaseklarhet

Det integrerade testet är ett **acceptanssteg, inte releasegodkännande**. Det verifierar transport, deklaration och viss normalisering men inte instansbaserad junctionlogik, topologisk semantik, exakta tillåtna kombinationer med relationstypsarv i `allowed_typed_pairs`, storskalig interoperabilitet mot externa verktyg eller komplett ArchiMate-konformitet.

**Rekommendation:** MMP 1.1 fortsätter vara **PARTIAL / NO-GO** till dess att de återstående semantiska och externa acceptanskraven har testats.
