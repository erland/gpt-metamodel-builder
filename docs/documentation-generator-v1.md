# Dokumentationsgenerator v1

Steg 7 genererar Markdown-dokumentation direkt från samma canonical YAML-paket som används av Sparx EA-generatorn.

## Omfattning

Generatorn dokumenterar:

- metadata och versionsnummer
- elementtyper
- relationstyper
- properties och enumerations
- constraints
- viewpoints
- notation
- provenance
- versions- och ändringsinformation

## Kommando

```bash
python3 scripts/generate_documentation.py examples/architecture-lite generated/architecture-lite-metamodel.md
```

## Principer

- Dokumentationen är genererad output och är inte canonical source.
- Samma input ska alltid ge byte-identisk Markdown.
- Dokumentation och MDG ska härledas från samma canonical modellversion.
- Generatorn ska inte lägga till semantik som saknas i canonical modellen.

## Referensartefakt

`generated/architecture-lite-metamodel.md`

## Test

`python3 scripts/test_documentation_generator.py`

Testet kör generatorn två gånger och kräver byte-identisk output samt verifierar representativa fragment från samtliga centrala dokumentationsdelar.
