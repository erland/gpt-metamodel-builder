# Strict MMP Core kandidatprofil på paketnivå

Status: **opt-in**, framtida Core-förslag. MMP 1.0.0:s normala inläsning är oförändrad.

`strict_core_candidate` (Python) och `strictCoreCandidate` (TypeScript) läser först fullständiga MMP-paket med befintlig importerande referenskonsument. Därefter valideras explicita kardinaliteter för relationernas båda ändpunkter och egenskaper samt konflikt mellan `required: true` och en övre gräns på noll.

Testmanifestet `conformance/package-semantic-manifest.json` innehåller separata `expected` (MMP 1.0.0) och `strict_expected` (opt-in strict). För tre schema-giltiga äldre paket är legacy `accept` men strict `reject`.

Detta innebär **inte** full strikt MMP Core-konformitet: relationstypsarv, instansantal, datatyp/default, kritiska extensionkrav och hela kravspecifikationen har ännu inte anslutits till en normativ strikt paket-gate. Testresultat får därför inte beskrivas som ett färdigt MMP 1.1-certifikat. Valet av strict måste vara explicit.
