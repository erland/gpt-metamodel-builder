# CORE-015 – Etapp 3: deterministisk subtype closure

Denna PR lägger till en separat Python-hjälpfunktion `scripts/mmp_effective_pairs.py` för att ta fram en sorterad, dubblettfri mängd konkreta tillåtna elementtypspar när en relation **uttryckligen** deklarerar `allowed_type_pairs`.

## Tolkning
- Om en deklarerad källa eller ett deklarerat mål är abstrakt räknas transitiva konkreta subtyper in. Även konkreta specialiseringar av konkreta typer räknas in.
- Multipelt **elementtypsarv** förenas som en mängd och dedupliceras.
- En abstrakt typ förekommer aldrig i den normaliserade listan.
- Saknad typ, arvscykel eller felaktig deklarerad endpoint avvisas.
- Om `allowed_type_pairs` saknas returneras ett uttryckligt fel; den äldre modellens `source.types` och `target.types` får inte tolkas som ett exakt tillåtet kartesiskt parset.

## Begränsningar
Detta är en **fristående analysfunktion**, ännu inte normativ paketsemanik: import/export och fristående Python-/TypeScript-konsumenter beräknar ännu inte samma effektiva par. Relationstypsarv, blandade föräldrar, relationer som ändpunkter, junctions och kardinalitet ingår inte. Ingen automatisk ändring eller migrering av gamla canonical YAML-filer görs.

## Fortsättning
Integrera och jämför samma effektiva parresultat i Python och TypeScript med gemensamma, fullständiga MMP 1.1-kandidat-fixtures; definiera först relationstypsarvets konfliktpolicy. CORE-015 är fortfarande PARTIAL och MMP 1.1 NO-GO.
