# Distribution av Metamodel Builder och engine

## Beslut

Metamodel Builder publicerar **sex projektartefakter**: en projekt-ZIP och fem
runtimepaket (Chat, Plugin, Claude Projects, Claude Skills och OpenCode).

En separat **Metamodel Builder-engine-ZIP rekommenderas inte**.
Distributionsmotorn är en delad, versionslåst komponent från GPT Byggaren och
har en egen officiell release, källrepo och checksumma. Att återpublicera den
som ett nytt projektunikt enginepaket skapar två oberoende uppdateringsspår
och oklarhet om vem som förvaltar säkerhetsfixar.

Projekt-ZIP ska innehålla kanonisk modell, projektstatus, domänskript,
scheman, tester, adapter och dokumentation. Den generiska enginearkitekturen
hämtas från GPT Byggarens versionerade release vid CI/release.

Om Metamodel Builder i framtiden behöver offlinebyggnad kan en **separat
nedladdningsbar build bundle** tillhandahållas med en oförändrad upstream
engine-ZIP, projekt-ZIP, låsta checksummor och verifieringsskript.
Den ska tydligt heta build bundle, inte en egen engineversion, och vara
frivillig; ingen enginekod kopieras in i runtimepaketen.

## Korrigering och återstående verifiering

- `validate-workspace` är ett av projektets elva deklarerade verktyg.
  Dess skript `scripts/validate_workspace.py` har nu explicit lagts till som
  resurs för Skill `metamodellering`, vilket gör att Plugin och Claude Skills
  kan packa samma verifierare som övriga runtimepaket.
- Claude Skills 1.2.0 har ett felaktigt `adapter.mode: openai_plugin` i
  `runtime-contract.json`. Orsaken finns i GPT Byggarens
  `claude_skills_runtime_contract`, som tidigare bara bytte runtime-ID.
- Korrigering av motorns källkod föreslås separat i
  [GPT Byggaren PR #97](https://github.com/erland/gpt-byggaren/pull/97).
  En ny officiell engine-release, med uppdaterat låst SHA-256, måste
  publiceras och tas i bruk innan nya Claude Skills-arkiv kan bli korrekta.
- Gamla releasearkiv 1.2.0 ändras inte i efterhand.
- Slutlig acceptans kräver nybyggda arkiv, kontroll av Claude-adapter,
  att alla elva verktygsresurser täcks av Skills och funktionstest med
  verkligen körda validerare och Sparx MDG-generatorn.
