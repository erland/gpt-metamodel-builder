# Steg 15 – Runtime parity och slutlig kvalitetssäkring

Status: **PASS**

## Verifierat
- ChatGPT Chat, ChatGPT Custom och OpenCode bygger från samma canonical projekt.
- Fyra kärnmarkörer finns i samtliga runtime-instruktioner.
- Capability-, artifact- och workspace/state-kontrakt är identiska.
- Tool-kontrakten är identiska efter normalisering av runtime-specifik execution-status.
- Custom GPT:s lokala scripts är explicit reducerade, inte felaktigt framställda som inbäddade verktyg.
- OpenCode har embedded Python-scripts och lokalt exekverbart flöde.
- Alla tre runtimepaketen byggs deterministiskt byte-för-byte.

## SHA-256
- ChatGPT Chat: `9725a8134306fb3330073334e3de9d36ce064904229a704c8f47e2dc4ae6116f`
- ChatGPT Custom: `45fe95483a52227f593cb4870490285d2d5547f996434758cb8ddcfaebeaea2f`
- OpenCode: `311d41cf4ede3820b5b88f0ca16f9bed3a83f598cef8a3b311d44eae6208b1ba`

## Medvetna plattformsskillnader
Se `docs/runtime-parity-v1.md`. Dessa är execution-/paketeringsskillnader och får inte ändra canonical modellsemantik eller artefaktkontrakt.
