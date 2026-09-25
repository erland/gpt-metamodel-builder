# Workflow-policy

## Syfte

Projektet är stateful. Strukturerad status och canonical filer är auktoritativa; konversationen är endast arbetsyta.

## States

- `idea_analysis`: behov och problemformulering.
- `architecture`: målarkitektur och kontrakt.
- `planning`: persistent utvecklingsplan.
- `implementation`: avgränsad implementation eller modelländring.
- `validation`: schema-, semantik- och plattformsvalidering.
- `packaging`: paketering av projekt och runtime-artefakter.
- `release`: release readiness och publicering.
- `maintenance`: fortsatt förvaltning efter release.
- `blocked`: blockerande fel eller saknat beroende.
- `paused`: verkligt verksamhetsbeslut krävs.

## Gates

- Ingen implementation markeras klar utan relevant deterministisk validering.
- Valideringsfel leder tillbaka till implementation.
- Packaging får starta först när aktuella valideringar passerar.
- Release får starta först när packaging är komplett.
- Status uppdateras först efter godkänd kontroll.

## Nästa steg

Nästa steg bestäms från faktisk status, blockerare och valideringsresultat, inte mekaniskt från föregående stegnummer.
