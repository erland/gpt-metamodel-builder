# Canonical metamodell v1

Canonical modellen är verktygsneutral och består av sju YAML-filer. Ingen målplattform får vara sanningskälla för semantiken.

## Filer

- `metamodel.yaml` – metadata, elementtyper, relationstyper och typ-arv.
- `properties.yaml` – datatyper, enumerations, property-definitioner och återanvändbara property sets.
- `constraints.yaml` – valideringsregler och deras allvarlighetsgrad.
- `viewpoints.yaml` – tillåtna element/relationer och syftet med olika vyer.
- `notation.yaml` – verktygsneutrala presentationsintentioner, inte Sparx-specifika Shape Scripts.
- `provenance.yaml` – källor och spårbarhet för härledda/importerade begrepp.
- `version.yaml` – semantisk version och förändringsmetadata.

## Referenser

ID-referenser valideras syntaktiskt i Steg 2. Att en refererad typ faktiskt finns och att arv är acykliskt kontrolleras i Steg 3 av den semantiska validatorn.

## Extension points

Där formatet behöver framtida utbyggnad finns explicit `extensions`. Verktygsspecifika uppgifter ska dock i första hand ligga i plattformsadaptern och inte i canonical modellen.

## Notation

Notation beskriver semantisk presentationsavsikt (t.ex. form och vilka egenskaper som bör visas). Exakta färgkoder, Shape Scripts, stereotype-metaclasses och toolbox-layout hör hemma i Sparx EA-adaptern.

## Provenance

Provenance anger källa, referens, härledningsrelation och valfri confidence. Den ska användas när modellen baseras på externa standarder, dokument, befintliga modeller eller importerad MDG.

## Versionering

Metamodellens `metamodel.version` och `version.current` ska representera samma logiska release. Konsistensen kontrolleras semantiskt i Steg 3.
