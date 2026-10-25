# MMP 1.1 – förslag till kompatibilitetsfrysning

**Status: kandidatbeslut, inte publicerat normativt kontrakt och inte release-GO.** Formatversion 1.0.0 förblir giltig och oförändrad. Denna granskning gäller endast den definierade, versionssatta 1.1-kandidatens semantik.

## Grundregel

En konsument måste tolka paket enligt paketets deklarerade version och dess obligatoriska, förhandlade profilversioner. En ny strikt valideringsprofil får aldrig tyst ge gamla paket en ny betydelse. Okänd obligatorisk profil ger `not_supported`, inte tyst godkännande.

## Tre kompatibilitetskänsliga beslut

| Område | Kontrakt att frysa inför 1.1 | Avgränsning |
| --- | --- | --- |
| Required + kardinalitet | `required:true` innebär effektiv undre gräns `max(deklarerat minimum,1)`; övre gräns ändras inte. En mindre uttrycklig maxgräns är ogiltig **när profilen krävs** | Om `default` kan uppfylla obligatoriskt värde är ännu inte beslutat. Gör inget sådant antagande |
| Kanoniska datavärden | Håll fast vid den tidigare avgränsade profilen för heltal, decimaltext, datum, UTC-datumtid i hela sekunder och begränsade HTTP(S)-URI:er | Detta är inte universell URI-normalisering eller full datatypexekvering |
| Exakta typade relationspar | Typnyckeln är exakt `{kind,id}`. Restriktioner från samtliga föräldrarelationer kombineras med snitt. Saknad föräldraprofil eller okända typer ska inte ignoreras | Ingen automatisk subtyputvidgning; framtida sådan tolkning kräver ny namngiven profil |

Detta formaliserar existerande kandidatbeteenden och tydliga avgränsningar; det inför inte nya wire-fält eller tysta ändringar i 1.0.

## Releasegrind

1. Frys paketversion och obligatoriska profilversioner med explicit förhandling och integritetsbindning.
2. Verifiera samma giltiga, ogiltiga och okända obligatoriska profiler i båda paketkonsumenterna.
3. Kör separata 1.0-regressionstester och ett enda gemensamt releasebeslut för 1.1:s **deklarerade** scope.
4. Dokumentera avgränsningarna i release notes och tydliggör att full modellinstansvalidering, avancerade junction-beteenden, härledning och regelmotor inte ingår.

## Återstående spärrar

- Bestäm och testa samspelet mellan `required` och `default`, alternativt märk detta uttryckligen som utanför 1.1-profilen.
- Säkerställ maskinläsbar profilförhandling och hela-paketparitet.
- Synkronisera föråldrade projektstatusfält i en releaseförberedande PR.

**GO/NO-GO:** Fortfarande **NO-GO**, tills ovanstående avgränsade releasegrind är verifierad.

Maskinläsbart beslutsunderlag: `conformance/mmp-1-1-compatibility-freeze-candidate.json`.
