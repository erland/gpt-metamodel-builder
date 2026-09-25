# Stateful workspace v1

Workspace är en separat, portabel projektyta som kan återupptas utan chatthistorik.

## Auktoritativ state
`workspace/state/workspace-state.yaml` anger workspace-identitet, canonical sökvägar, aktuell progression, valideringsgates och resumekrav.

`workspace/state/change-log.yaml` är en append-only orienterad ändringshistorik för tillämpade workspace-händelser.

## Resume-regel
Vid återupptagning ska GPT:n först läsa workspace-state, verifiera alla `required_paths`, läsa ändringsloggen och därefter läsa endast de canonical filer som behövs för nästa avgränsade åtgärd. Konversationen får inte krävas för att förstå aktuell status.

## Gate
State får uppdateras till ett nytt lyckat läge först efter relevant deterministisk validering. Vid fel ligger tidigare godkänd state kvar och åtgärden markeras blockerad/pending tills felet är korrigerat.
