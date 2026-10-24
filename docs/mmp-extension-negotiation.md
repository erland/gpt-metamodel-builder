# MMP extensions – separat kapabilitetsförhandling

Status: **förslag för MMP 1.1**, inte en ändring av publicerad MMP 1.0.0. Paketets `manifest.yaml` och `extensions`-objekt modifieras inte.

En producent kan beskriva **nödvändiga** och **frivilliga** tillägg med identifierare (URI) och exakta versionsnummer i en **separat förhandlingsdeklaration**. Konsumenten deklarerar stödda kombinationer av tilläggs-ID och version.

Vid förhandling returneras:
- `supported` om alla begärda tillägg stöds.
- `partial` om alla nödvändiga men inte samtliga frivilliga tillägg stöds; lista frivilliga tillägg som inte kan tolkas.
- `not_supported` om något nödvändigt tillägg saknar exakt versionsmatchning; en konsument ska då inte hävda semantiskt korrekt full import.

Okända frivilliga tillägg får bevaras ointerpret­erade, men inte exekveras eller räknas som implementerade. Denna förhandling ska ske innan någon specifik semantik från tilläggen används.

**Viktiga begränsningar:** Deklarationen är ännu inte signerad eller bunden kryptografiskt till ett enskilt MMP-paket. Den är därför inte i sig ett säkert sätt att påstå att paketet kräver en viss semantik. Versionsmatchning är avsiktligt exakt; SemVer-intervall och beroenden mellan extensions behöver framtida förhandling. Inga av dessa krav får retroaktivt antas följa av MMP 1.0.0.

Gemensamma testfall finns i `interop/extension-negotiation-v1.json`, testade av oberoende Python- och TypeScript-funktioner.
