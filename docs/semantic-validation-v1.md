# Semantisk validering v1

Steg 3 kompletterar JSON Schema med deterministiska kontroller över de sju canonical YAML-filerna.

## Kontroller

Validatorn kontrollerar bland annat:

- unika ID:n i canonical samlingar och enum-värden,
- att element- och relationstyper inte skapar tvetydiga typ-ID:n,
- att `extends` refererar till befintliga typer och inte bildar arvscykler,
- att relationers source/target refererar till befintliga elementtyper,
- att property sets och property-definitioner kan lösas,
- att custom datatyper och enumerations finns,
- att enum-defaultvärden är giltiga,
- att `required: true` inte kombineras med kardinalitet som tillåter noll värden,
- att viewpoints refererar till definierade typer och är slutna över relationernas endpoints,
- att required viewpoint-element även är allowed,
- att notation refererar till befintliga element/relationer/properties,
- att constraints refererar till rätt typ av objekt,
- att property-referenser i deklarativa constraints finns,
- enkla deterministiskt identifierbara motsägelser mellan deklarativa constraints,
- provenance-källor och targets,
- att `metamodel.version` och `version.current` är konsistenta.

## Rapportformat

`scripts/validate_semantics.py` skriver maskinläsbar JSON till stdout och kan även skriva samma rapport med `--json-out`.

Exit code `0` betyder att inga semantiska errors hittades. Warnings påverkar inte exit code. Exit code `1` betyder att modellen inte får gå vidare till generering.

## Avgränsning

Validatorn försöker inte tolka fri naturlig text eller full OCL-semantik. Avancerad constraint-exekvering är ett senare utbyggnadsområde. I v1 valideras referenser och ett begränsat deklarativt uttrycksformat deterministiskt.
