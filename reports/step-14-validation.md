# Steg 14 – valideringsrapport

Status: **PASS**

## Leverabler
- `scripts/build_opencode_runtime.py`
- `scripts/validate_opencode_runtime.py`
- `assistant/policies/opencode-runtime.md`
- `docs/opencode-runtime-v1.md`
- OpenCode ZIP med `AGENTS.md`, `opencode.jsonc`, primär agent och två skills

## Kontroller
- OpenCode runtime validation: PASS
- Kärnmarkörer i AGENTS.md: PASS
- Default agent: PASS
- Skills discovery-struktur: PASS
- Inbäddade runtime scripts: PASS
- Manifest/checksummor: PASS
- Deterministiskt ZIP-bygge: PASS (identisk SHA-256 för två byggen)
- Project foundation contract: PASS
- Model robustness: PASS
- Lint: PASS, 0 fel och 0 varningar
- Hygiene: PASS

## Plattformskontrakt
OpenCode V2 använder root `AGENTS.md` för aktiva projektinstruktioner. Projektlokala agenter ligger under `.opencode/agents/` och skills under `.opencode/skills/`. Ingen modellleverantör hårdkodas i distributionen.
