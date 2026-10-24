# MMP cardinality and required – interoperabilitetsprofil (förslag)

Status: **fristående tolknings- och testprofil**, inte ändring av publicerad MMP 1.0.0. JSON Schema-validering och semantisk strikt validering är separata steg.

Kardinalitet uttrycker multiplicitet med `*` (0..obegränsat), ett icke-negativt heltal `n` (exakt n), `n..m` (inklusive gränser), och `n..*` (min n). Endast ASCII-siffror, inga inledande nollor (utom `0`) och inga blanksteg. `min <= max` är semantiskt krav i en framtida strikt profil. `max = null` i testvektorer betyder obegränsat, inte ett värde i MMP-filen.

`required: true` innebär närvaro av minst ett värde men formatet har inte beslutat hur detta samverkar med `cardinality: 0..*`. Vår konservativa **profilkontroll** redovisar därför detta som `undecided` och gör **ingen** retroaktiv avvisning. `required: false` upphäver inte ett uttryckligt minimiantal. Ett saknat kardinalitetsfält ger inte implicit max 1. Defaultvärden och deras datatyp valideras i en senare separat profil.

Testvektorerna finns i `interop/cardinality-v1.json`. Båda konsumenternas hjälpfunktioner använder samma definierade semantik men aktiverar **inte** nya avvisningsregler under MMP 1.0.0-inläsning. Därmed förblir accept/reject-baslinjen oförändrad.

Öppet beslut inför strikt Core-konformitet: ska `required:true` tillsammans med `min=0` innebära effektivt minimum 1, eller avvisas som inkonsekvent? Vi reserverar beslutet i stället för att bygga in oavsiktlig kompatibilitetsbrytning.
