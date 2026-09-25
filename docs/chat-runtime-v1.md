# ChatGPT Chat-runtime v1

Chat-distributionen är en portabel körprofil för Metamodel Builder. Den innehåller canonical instruktion, policies, schemas, mallar, dokumentation och deklarerade deterministiska scripts.

## Återupptagning
Ett användarworkspace ska kunna återupptas från filerna i `workspace/`, i synnerhet `state/workspace-state.yaml` och `state/change-log.yaml`. Chatthistorik är inte nödvändig.

## Leveransprincip
När en faktisk metamodell ändras ska den uppdaterade workspace-/projekt-ZIP:en vara leverabeln. MDG XML och dokumentation regenereras från canonical källor.
