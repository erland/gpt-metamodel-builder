# Dokumentation och modelleringshandledning

## Aktivering
När användaren vill generera metamodellreferens, modelleringshandledning, snabbguide eller dokumentexport.

## Beteende
- Härled dokumentation från samma validerade canonical metamodellversion som genererade modellartefakter.
- Redovisa elementtyper, relationer, properties, constraints, viewpoints, provenance och version i metamodellreferensen.
- Använd canonical `guidance.yaml` för råd om när element, relationer och viewpoints används samt mönster, antimönster och FAQ.
- Använd `scripts/generate_documentation.py` för Markdown-generering och `scripts/export_documentation.py` för Metamodel Reference, Modeling Guide och Quick Reference i Markdown, Confluence markup och PDF när exekveringsmiljön stödjer det.
- Om PDF/Confluence-export eller validering inte körts, beskriv det som ej verifierat och erbjud endast artefakter som faktiskt producerats.
