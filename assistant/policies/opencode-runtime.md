# OpenCode runtime-policy

## Runtime

OpenCode är den lokala, fullt exekverbara runtime-varianten för Metamodel Builder. Projektets root är workspace och `AGENTS.md` är aktiv projektinstruktion.

## Regler

- Kör deterministiska validators och generatorer via Python-scripten i `scripts/`.
- Läs `workspace/state/workspace-state.yaml` före en stateful ändring.
- Gör ändringar i canonical YAML eller plattformsadapter; redigera aldrig genererad MDG XML som sanningskälla.
- Kör relevant validering före statusuppdatering.
- Använd Git-diff/status för att granska förändringar när workspace är ett Git-repo.
- Modifiera inte användarens Git-historik automatiskt; commit/push görs endast när användaren uttryckligen begär det.
- Om ett externt standardunderlag används ska provenance bevaras.
