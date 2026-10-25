# MMP – formellt versions- och kompatibilitetsbeslut inför release

**Beslut:** behåll publicerat paketformat **MMP 1.0.0**. De vidareutvecklade reglerna är i nuläget **frivilliga kandidatprofiler**, inte ett nytt normativt MMP 1.1.0-kontrakt. Versionsbeslutet finns maskinläsbart i `conformance/mmp-version-decision-v1.json`.

## Stabilt kontrakt

Oförändrade sju obligatoriska kanoniska entrypoints, manifest, medlemsinventering, kontrollsummor och referenser till lokala JSON Schemas. Identiteten är fortsatt namespace + lokalt ID. Ordinarie konsumentvalidering för 1.0.0 behåller sitt befintliga accepteringsbeteende och ska inte få striktare semantik implicit.

## Frivilliga tillägg utan nytt paketformat

Den föreslagna `strict-core-candidate` är ett **explicit val** som validerar en delmängd av kardinalitets- och required-regler efter ordinarie paketläsning. Referenskonsumenternas hjälpfunktioner för datatyper, kanoniska värden, relationstypsarv, extensions och modellversioner ger ytterligare delresultat, men de är inte ett komplett kravpaket. Profilerna `mmp-rules`, `mmp-notation` och `mmp-viewpoints` saknar verifierad full konformitet.

## Vad vi inte beslutar

Vi publicerar **inte** `package_format_version: 1.1.0`, ändrar **inte** befintliga schemas och lovar **inte** fullständig strikt Core-konformitet. Kritiska extensions, nya obligatoriska fält eller inkompatibel betydelseändring av existerande fält kräver separat förhandling och explicit versionsbeslut, möjligen en ny major-version.

## Releasebeslut och nästa leverans

En användbar **MMP Specification Kit 1.0.0** kan genomgå ett slutligt acceptanstest och publiceras med korrekt begränsade konformitetsanspråk. Nästa steg är releasekandidatgranskning: bygg artefakten deterministiskt, kontrollera SHA-256, kör paketbaserade tester i båda oberoende konsumenterna och granska att ingående profilförslag uttryckligen är icke-normativa.

MMP 1.1.0 har tills vidare **NO-GO**. Detta är inte en kvalitetsbrist hos 1.0.0 utan ett avgränsningsbeslut för att inte blanda ett stabilt utbytesformat med ofärdiga semantiska profiler.
