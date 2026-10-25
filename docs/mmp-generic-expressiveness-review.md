# Generisk uttrycksförmåga – samlad intern bedömning

**Status: PARTIAL / NO-GO för full MMP 1.1-konformitet.** Bedömningen är en spårbar ögonblicksbild av källkod och registrerade syntetiska acceptanstester, inte en certifiering eller ett löfte om stöd för ett externt modelleringsspråk.

## Testad deklarativ täckning

| Område | Evidensnivå | Vad som faktiskt prövas |
| --- | --- | --- |
| Stor typkatalog | Paket/roundtrip | 49 tillförda elementtyper, 7 relationstyper, 2 junctiontyper och 5 047 tillåtna typade par |
| Informationsbevarande | Innehållsrevision | ID-mängder, innehållsdigests och exakta par per relationstyp; även negativa mutationsfall |
| Multipelt elementarv | Kandidatpaket/roundtrip | Abstrakt bastyp och flera föräldrar bevaras |
| Multipelt relationsarv | Instansgranskning | Restriktivt snitt av exakta typade par i Python och TypeScript |
| Relation som ändpunkt | Instansgranskning | En acyklisk relationsinstans refererar till en annan |
| Junctions | Strukturell profil | Förhandlade operatorvärden och in-/utgående strukturella kanter, inte operatorbeteende |

Evidenshänvisningarna finns maskinläsbart i `conformance/mmp-generic-expressiveness-post-advanced.json`. Tester skiljer uttryckligen mellan transport/roundtrip och verifierad instanssemantik.

## Vad som inte är styrkt

- Full normalisering eller subtyputvidgning i alla kombinationer av multipelt arv och typade relationspar.
- Fullständiga regler för kardinalitet, komplett instanspopulation och rekursiva relationskedjor.
- Beteendesemantik för olika junctionoperatorer eller härledning av indirekta relationer.
- Required-policy, kanoniska värden och generella exekverbara regler (CORE-009/011/012).
- Oberoende extern interoperabilitet eller fullständig språkkonformitet.

## Nästa beslut

Prioritera **CORE-009/011 med normativa, språkneutrala värde- och required-testvektorer**. Håll stöd och releasebeslut åtskilda: stora syntetiska modeller visar formatets deklarativa kapacitet, men kan inte ensamma motivera en stabil MMP 1.1-release.

Ingen ändring av canonical YAML eller MMP 1.0 görs i denna granskning.
