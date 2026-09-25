# Modeling guidance v1

`guidance.yaml` är canonical källa för praktisk modelleringshandledning. Den är verktygsneutral och separerad från Sparx EA-adaptern.

## Innehåll

- övergripande modelleringsprinciper och namngivningsregler
- när varje elementtyp ska respektive inte ska användas
- goda/dåliga namnexempel och vanliga misstag
- semantik och användningsråd för relationstyper
- viewpoint-guide med arbetsgång och frågor som vyn besvarar
- modelleringsmönster och antimönster
- FAQ

## Genererade dokument

`export_documentation.py` skapar tre dokumenttyper från samma canonical modell:

1. **Metamodel Reference** – teknisk referens över metamodellen.
2. **Modeling Guide** – praktisk handledning för modellerare.
3. **Quick Reference** – kort beslutsstöd för vardaglig modellering.

Varje dokument kan exporteras som Markdown, Confluence wiki markup eller PDF. PDF-exporten använder ReportLab i exekverbara runtimes.

## Princip

Vägledning ska inte dupliceras manuellt i respektive exportformat. Ändra `guidance.yaml`, validera modellen och regenerera alla dokument.
