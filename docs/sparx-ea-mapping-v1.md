# Sparx EA mapping-model v1

## Syfte

Mapping-modellen isolerar Enterprise Architect-specifika konstrukt från den verktygsneutrala metamodellen. Den är avsedd att vara input till MDG-generatorn i Steg 5.

## Struktur

`mapping.yaml` är manifest och deklarerar Technology/Profile-metadata, UML-metaclasses samt namn på adapterfiler. Övriga filer hanterar stereotypes, Tagged Values, diagramprofiler, toolboxprofiler, Quick Linker och Shape Scripts.

## Designregler

1. Varje stereotype pekar på exakt ett canonical element eller en canonical relation.
2. Base metaclass måste vara deklarerad i mapping-manifestet och ha rätt kind (`element`, `connector`, `diagram`).
3. Tagged Values pekar på canonical property definitions.
4. Diagramprofiler pekar på canonical viewpoints.
5. Toolboxinnehåll pekar på definierade stereotypes/relationer.
6. Quick Linker-regler måste överensstämma med canonical relationens source/target.
7. Shape Script-indexet pekar på canonical objekt och existerande scriptfiler.
8. Technology-versionen måste överensstämma med canonical metamodellversion.

## Avsiktlig avgränsning

V1 definierar en generatorvänlig intern mappningsmodell, inte den slutliga MDG XML-strukturen. Exakt XML-rendering, namespace-detaljer och paketering hör till Steg 5.
