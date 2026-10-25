# Required, default och instansnärvaro – kandidatkontrakt för MMP 1.1

**Status:** opt-in kandidat `mmp-required-default-presence@0.1.0`, **inte** normativ 1.1-release eller retroaktiv regel för 1.0. Den här profilen testar endast det avgränsade beslutet om en värdesatt egenskap räknas som uttryckligen angiven.

## Beslut

- `required: true` innebär att minst ett **uttryckligen angivet, icke-null värde** måste finnas i en instans. Ett deklarerat `default` räknas **inte** som instansnärvaro, oavsett om standardvärdet senare kan användas för presentation eller beräkning.
- Ett deklarerat positivt kardinalitetsminimum måste uppfyllas även med `required: false`; standardvärden reducerar inte detta krav.
- `required: false`, min=0 och inget angivet instansvärde godtas; ett standardvärde är då endast *tillgänglig fallback-metadata*, inte ett implicit lagrat värde.
- `null` betraktas inte som ett angivet giltigt värde. En tom lista innehåller noll värden; en skalär ett. Explicit maxgräns kontrolleras.
- Om `required: true` strider mot explicit max=0 är **profilkontraktet ogiltigt**.
- Profilens närvarokontroll utför inte datatypskontroll av default, kanonisering, automatisk materialisering eller full instansvalidering; sådana garantier kräver egna förhandlade profiler.

## Kompatibilitet

Det här är en **tillagd frivillig semantisk policy**. Import/export, `package_format_version: 1.0.0` och äldre default-värdesregler förblir oförändrade. Före stabil publicering måste profilen få versionerat paketmanifest, integritetsbindning och hela-pakettest i Python/TypeScript; dessa tester är fortfarande en kandidatprototyp.

Gemensamma positiva och negativa vektorer ligger i `interop/required-default-presence-v1.json` och körs i båda språkens CI. Ingen koppling till ett externt modelleringsspråk görs.

**Releasebeslut för full MMP 1.1: NO-GO.**
