# CORE-016 – fullständigt kandidatpaketprov för ärvda typade par

Detta integrerade prov bygger en **riktig MMP 1.1-kandidat** från en ArchiMate-neutral metamodell med multipelt relationstypsarv. Det kör export, paketvalidering, oberoende Python-konsument, import/byteidentisk canonical roundtrip och faktiska instansgrafskontroller. TypeScript-workflow kör dessutom den fristående MMP-konsumenten och instansgrafevaluatorn på modell och fixtures från den importerade kandidaten.

Testerna omfattar ett tillåtet ärvt instanspar, otillåten källa och otillåtet mål, ofullständig graf samt saknat föräldrakontrakt. Förbjuden MMP 1.0-export verifieras uttryckligen. Inget produktionsschema eller exportformat ändras.

**Avgränsning:** Detta är ett syntetiskt acceptansscenario för redan definierad exakt snittsemantik och inte en full konformitetscertifiering. Full validering av relationstyps-/elementarv i alla domäner, externa konsumenter och ArchiMate-fall återstår. MMP 1.1 förblir **PARTIAL / NO-GO**.
