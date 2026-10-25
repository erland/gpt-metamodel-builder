# MMP 1.1 – avgränsad versions- och omfattningsfrysning

**Beslutsstatus: föreslaget kontrakt för release, fortsatt NO-GO.** Detta steg fryser vilket kontrakt vi tänker publicera, men ändrar inte nuvarande paketering, MMP 1.0 eller befintlig Specification Kit.

## Versionerna får inte förväxlas

- **Paketformat:** `mmp`, kandidat till stabil `package_format_version: 1.1.0`.
- **Befintligt Specification Kit:** `1.1.0`, men dess `mmp-kit/version.json` anger alltjämt **paketformat 1.0.0**.
- **Föreslagen nästa kit-version:** `1.2.0`, reserverad för en framtida distribution med det godkända 1.1.0-kontraktet. Kit-numret är ett förslag tills ett separat bygg-/publiceringsbeslut fattas. **Skriv inte över befintligt kit 1.1.0.**

## Minsta garanterade 1.1-kontrakt

Manifest och kanonisk metamodell deklarerar identiska obligatoriska profil-ID:n och versionsnummer. Ett paket får bara betraktas som tolkat om konsumenten stöder **alla** obligatoriska kapabiliteter. Okända versioner är `not_supported`, inte tyst acceptans.

1. Befintliga kanoniska entrypoints och innehållsintegritet bevaras.
2. Typdefinitioner, typade ändpunkter, junctiontyper och exakta typade relationspar roundtrippas utan förlust.
3. Relationsarv följer den deklarerade kandidatprofilens restriktiva snitt för **exakta** typpar. Ingen automatisk subtyputvidgning.
4. Junctionprofilens operatorer är **strukturmetadata**; AND/OR-beteende ingår inte.
5. Required/default-närvaroprofilen kräver uttryckliga instansvärden för `required:true`; deklarerad `default` räknas inte som sådan närvaro.
6. 1.0.0-paket behåller exakt sitt tidigare tolkningskontrakt.

Profiler och exakta versioner finns i `conformance/mmp-11-version-scope-freeze.json`.

## Inte del av 1.1-kontraktet

Full instansgrafs-/kardinalitetsvalidering, automatisk subtypsexpansion, junctionaktivering, generell relationshärledning och regelspråk samt universell URI- eller datatypskanonisering kräver uttryckliga framtida profiler. De får inte införas som retroaktiv omtolkning.

## Evidens och releasekriterier

PR #92 är mergad och dess CI, TypeScript-interoperabilitet och preflight rapporterade PASS. Det kombinerade pakettestet i `scripts/test_mmp_11_combined_profiles_package.py` verifierar flera samtidiga obligatoriska profiler. Detta är inte bevis för fullständig Core-konformitet.

**Fortfarande NO-GO:** En ny versionerad, reproducerbar Specification Kit-distribution med release-tag, kontrollsummor och slutlig projektstatus/releaseinformation återstår. Först därefter kan beslutet ändras till GO.
