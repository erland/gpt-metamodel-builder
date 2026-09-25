# Sparx EA MDG generator v1

Steg 5 inför den första deterministiska generatorn från canonical YAML + Sparx EA-adapter till en MDG Technology XML.

## Ingångar

- canonical metamodell (`examples/.../*.yaml`)
- Sparx EA mapping-model (`platforms/sparx-ea/*.yaml`)

## Genererad struktur

Generatorn skapar:

- `MDG.Technology` + Technology Documentation
- en UML Profile med stereotypes och `AppliesTo`
- inline Tagged Values
- Quick Linker-regler som `stereotypedrelationships`
- Diagram Profile
- Toolbox Profile
- generator-metadata för spårbarhet

## Avgränsning i v1

Shape Scripts finns i adaptern men bäddas ännu inte in i MDG-filen. Sparx lagrar exporterade Shape Scripts i en kodad form och den delen tas i Steg 6 tillsammans med djupare MDG-validering och praktisk importverifiering.

Detta är medvetet: Steg 5 etablerar den deterministiska vertikala kedjan och Steg 6 höjer Sparx-formatets fidelity.

## Determinism

Samma canonical modell och adapter ska ge byte-identisk XML. `scripts/test_mdg_generator.py` genererar därför samma fil två gånger och jämför SHA-256.
