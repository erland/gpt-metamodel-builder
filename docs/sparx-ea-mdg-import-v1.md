# Sparx EA MDG import v1

Steg 8 inför reverse engineering från en befintlig Sparx Enterprise Architect MDG Technology XML till två nivåer:

1. **Intermediate representation** i `intermediate/mdg-import.yaml` som bevarar Sparx-specifika uppgifter och importbegränsningar.
2. **Canonical projection** i `canonical/` samt en rekonstruerad `platforms/sparx-ea/`-adapter.

Importeraren läser teknikmetadata, UML-profilens stereotyper/metaclasses, Tagged Values, materialiserade Quick Linker-relationer, diagramprofiler, toolboxprofiler och inbäddade `EAShapeScript 1.0`-payloads. Shape Scripts packas upp till redigerbara `.shape`-filer.

## Fidelity

Följande kan bevaras med hög fidelity när informationen finns i MDG XML:

- tekniknamn och version
- stereotype-namn och bas-metaclass
- element/connector-klassificering
- Tagged Values och enum-värden
- riktade relationer
- Quick Linker source/target/relationship när de materialiserats som `stereotypedrelationships`
- diagramnamn och diagram-metaclass
- toolbox-sidor och poster
- Shape Scripts

Följande markeras uttryckligen som approximation i v1:

- exakt canonical betydelse/kind för importerade stereotype-begrepp
- ursprunglig grouping/id-struktur för toolboxar när den inte kan härledas entydigt
- exakt allowed content för viewpoints/diagram
- constraints och semantik som aldrig var kodade i MDG-filen

Importerad canonical modell ska därför ses som ett granskningsbart utkast, inte som bevis för den ursprungliga designintentionen.
