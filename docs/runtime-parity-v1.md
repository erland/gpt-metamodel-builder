# Runtime parity v1

Metamodel Builder har fyra aktiverade peer runtimes: ChatGPT Chat, ChatGPT Custom, OpenCode och OpenAI Plugin. Alla härleds från samma canonical projekt och måste behålla samma semantik, artefaktkontrakt, workspace/state-kontrakt och verktygsdefinitioner.

## Paritetskrav

Följande måste vara identiskt mellan runtimes:

- kärnprinciperna i canonical instruktion,
- canonical metamodellens semantik,
- artefaktkontrakt,
- workspace/state-kontrakt,
- verktygs-ID:n, syften och deterministiska egenskaper,
- reglerna att canonical YAML är sanningskälla och att genererad MDG inte är source,
- validering före progression.

## Tillåtna plattformsskillnader

| Område | ChatGPT Chat | ChatGPT Custom | OpenCode | OpenAI Plugin |
|---|---|---|---|---|
| Canonical semantik | Full | Full | Full | Full |
| Stateful workspace via filer | Full | Full | Full | Krävs från host |
| Inbäddade projekt-scripts | Ja | Nej | Ja | Ja, som skill-resurser |
| Deterministisk lokal exekvering | När runtime kan köra scripts | Reducerad; Data Analysis är fallback | Full lokal Python/shell | Hostberoende Python/code execution |
| Git-integration | Inte en del av kontraktet | Inte en del av kontraktet | Valfri lokal Git | Inte en del av kärnkontraktet |
| Knowledge/reference-paket | Fullt runtimepaket | Prioriterat 20-filspaket | Lokala docs/examples | Schemas, modell, adapter, docs/examples och workflow-reference |

Skillnaderna ovan får inte förändra modellsemantik eller låta en runtime påstå att en kontroll passerat när den inte faktiskt körts.

## Automatisk parity-gate

`scripts/validate_runtime_parity.py` bygger på runtime-kontraktens snapshots och verifierar:

1. alla kärnmarkörer finns i runtime-instruktionen,
2. capability-, artifact- och workspace/state-kontrakten är identiska,
3. verktygskontrakten är identiska efter att runtime-specifik execution-status normaliserats,
4. OpenCode verkligen har embedded scripts,
5. OpenAI Plugin är skills-first/workspace-first, har paketerade script-resurser utan MCP-krav och deklarerar `equivalent_runtime_dependent`,
6. Custom GPT:s lokala scriptverktyg är markerade som reducerade.

Denna gate ska köras efter att alla fyra runtimepaketen byggts och före release.
