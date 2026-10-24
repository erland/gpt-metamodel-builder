# Källanpassning

## Aktivering
När metamodellen ska utgå från ArchiMate, UML, BPMN, TOGAF-relaterat material eller annan extern specifikation/modell.

## Beteende
1. Använd aktuellt och tillåtet källmaterial; skilj mellan standardens egna begrepp och projektets egna specialiseringar.
2. Normalisera relevanta begrepp till ett granskningsbart source catalog.
3. Skapa en adaptation plan med `status: draft`, där behållna, omdöpta, specialiserade och utelämnade begrepp tydligt redovisas.
4. Kräv verksamhetsmässigt godkännande innan planen skrivs in som canonical output.
5. Applicera därefter planen deterministiskt med `scripts/adapt_source_model.py` när körmiljön stöder det.
6. Bevara provenance för varje härlett element och relation; validera schema och semantik.

Distribuera aldrig kompletta tredjepartsspecifikationer utan klar licensgrund. Vid ofullständigt underlag, redovisa osäkerheter som granskningsbara utkast.
