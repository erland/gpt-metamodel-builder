# Intern utökad strukturfixture

Denna syntetiska testmodell prövar generell uttrycksförmåga i MMP 1.1-kandidaten utan anspråk på kompatibilitet med eller representation av något externt modelleringsspråk. Testet genereras temporärt och är ingen produktmodell.

Den innehåller en abstrakt basklass, två ärvande typer och en typ med multipelt arv; två restriktiva föräldrarelationer och en barnrelation med ärvt snitt; en relation med en annan relationsinstans som mål; samt två deklarerade junctiontyper med operatorer lagrade enbart i en förhandlad profil.

Acceptanstestet verifierar kandidatpaketets export, validering, import, byteidentisk canonical roundtrip, profiltransport, korrekt multipelt relationsarv, faktisk typad instansgraf och positiva/negativa junction-strukturfall. Python och TypeScript kör samma instansfall. Den separata strukturella junction-kontrollen säger ingenting om exekvering eller fullständigt beteende för operatorer.

Äldre relationer i referensmodellen är oförändrade och utelämnas ur den opt-in typade instansgrafvalideringen. De finns kvar i det fullständiga exporterade paketet. Ingen ändring görs av canonical schema eller MMP 1.0.

**Avgränsning:** Inget normativt ställningstagande om subtyputvidgning, härledning eller avancerad flödessemantik. MMP 1.1 förblir PARTIAL / NO-GO.
