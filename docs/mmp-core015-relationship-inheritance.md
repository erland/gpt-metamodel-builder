# CORE-015 – relationstypsarv och flera föräldrar (kandidatregel)

## Semantik i denna etapp
Funktionen `scripts/mmp_effective_pairs.py` beräknar effektiva par genom att först expandera deklarerade par till konkreta elementtyper. För en relation med en eller flera föräldrar används **snittet** av alla tillämpliga föräldrars parrestriktioner och relationens egen explicita restriktion om sådan finns. Relationens egna endpoint-mängder begränsar sedan resultatet till tillåtna konkreta undertyper. Ingen dold union/vidgning med flera föräldrar sker.

Om arvsgrafen innehåller en cykel, en okänd förälder, saknad explicit pairwise-semantik i en ärvd förälder eller tomt snitt avvisas beräkningen med tydligt fel.

## Bakåtkompatibilitet
Äldre canonical YAML ändras inte, och vanliga relationer utan deklarerade par fortsätter använda äldre semantik. Funktionen är opt-in och får inte fabricera tillåtna par genom `source.types × target.types`. Ingen automatisk YAML-migrering sker. Vid framtida migration måste relationstypsarv analyseras och tvetydiga gamla modeller rapporteras för manuell granskning.

## Begränsning
Endast den fristående Python-analysfunktionen har denna policy i PR:en. Python/TypeScript-konsumenterna använder fortfarande den tidigare explicita-par-semantiken utan relationstypsarv. Konsumentparitet och fullpaketstest av arv är nästa steg. Detta är **inte** fullständig CORE-015-konformitet, och MMP 1.1 är fortfarande NO-GO.
