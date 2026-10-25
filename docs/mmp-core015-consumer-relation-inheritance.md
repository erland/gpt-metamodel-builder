# CORE-015 – relationstypsarv i oberoende MMP-konsumenter

## Ändring

Python och TypeScript beräknar nu samma `effective_pairs` för MMP 1.1-kandidatpaket med ärvda pairwise-regler. Varje förälder begränsar tillåtna typkombinationer. Vid multipelt relationstypsarv används snittet, därefter begränsas paren till barnrelationens ändpunktstyper. Explicita barnpar är ytterligare försnävningar. Resultatet är deterministiskt sorterat och dubblettfritt.

En förälder utan uttryckligt pairwise-kontrakt, okända föräldrar, arvscykler och tomma tillåtna mängder avvisas när pairwise-profilen faktiskt används. Detta motsvarar tidigare beslutad konservativ policy i `scripts/mmp_effective_pairs.py`.

## Paketbaserad verifiering

`scripts/test_mmp_relation_inheritance_package.py` genererar ett verkligt MMP 1.1-kandidatpaket med två föräldrarelationer, en specialisering samt konkreta undertyper. Det jämför Python/TypeScript mot den fristående normaliseringsfunktionen, gör import/roundtrip utan att skriva över canonical YAML och säkerställer att äldre MMP 1.0-export inte förlorar regler. CI och TypeScript-workflow kör båda positiva verifieringarna.

## Migrering och kvarstående frågor

Äldre YAML-modeller får inga nya fält och behöver ingen automatisk migrering. Relationer som saknar pairwise-profil får inga underförstådda par. För en äldre modell som ska uppgraderas måste explicita tillåtna par och relationstypsarv granskas före aktivering av profilen; någon kartesisk produkt får inte konstrueras som tyst default.

Denna etapp täcker inte typade relationer eller junctions som ändpunkter (CORE-016), instanskardinalitet eller hela ArchiMate-fallet. MMP 1.1-konformitet är fortfarande PARTIAL/NO-GO.
