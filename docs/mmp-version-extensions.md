# MMP – versionskompatibilitet och extensions (förslag)

Status: **fristående semantisk profil**, inte ändring av publicerade MMP 1.0.0-scheman.

## Två versionsaxlar
`package_format_version` styr formatkompatibilitet; `metamodel.version` är modellens egen version. Dessa ska inte blandas ihop. `version.yaml:version.compatibility.level` är producentens deklaration, inte ett automatiskt bevis på konsumentkompatibilitet.

## Konservativ förändringsklassificering
- `breaking`: namnrymdsbyte eller borttagning av tidigare existerande element-/relationstyp-ID.
- `compatible`: ändrad visningsetikett/beskrivning eller tillagd typ utan andra förändringar i kvarvarande typdefinitioner.
- `needs_review`: övriga ändringar på befintliga typdefinitioner, inklusive kind, endpoints, arv, obligatoriska egenskaper eller extensions. Bedömningen får inte tyst betraktas som kompatibel.

Denna minimalprofil klassificerar inte ännu property definitions, datatyper, standardvärden eller versionshistorik. Ett komplett kompatibilitetsbesked kräver senare utökning; `compatible` gäller här **endast de granskade typdefinitionerna** och får inte användas som total kompatibilitetsgaranti för en hel MMP.

## Extensions
MMP 1.0.0:s `extensions` är ett fritt objekt utan inbyggd obligatorisk/valfri markering. Konsumenten får bevara okända värden utan att exekvera dem och deklarera `preserved_uninterpreted`. Om **separat överenskommen profil** anger att ett okänt tillägg är kritiskt, rapporteras `not_supported`; inga externa criticality-antaganden görs om paketets 1.0.0-innehåll. Kända tillägg rapporteras `supported` enbart om de finns i den uttryckliga igenkänningslistan, inte automatiskt för att JSON parsas.

Se `interop/version-extension-v1.json` för positiva och negativa tvärspråkstester. Profilerna påverkar inte den befintliga MMP 1.0.0-importören.
