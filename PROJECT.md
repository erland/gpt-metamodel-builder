# PROJECT

## Projektnamn
Metamodel Builder

## Syfte
Skapa och förvalta verktygsneutrala metamodeller med canonical YAML som sanningskälla och med Sparx Enterprise Architect MDG Technology som första fullständiga exportformat.

## Arkitekturbeslut
- Canonical semantik är verktygsneutral.
- Sparx EA är en separat plattformsadapter.
- Projektet är stateful och ska kunna återupptas från projekt-ZIP.
- Genererade artefakter är aldrig canonical source.
- Provenance ska bevaras vid import och härledning från externa standarder.
- ChatGPT Chat, ChatGPT Custom och OpenCode är aktiverade mål-runtimes i v1.

## Nuvarande fas
Alla 16 planerade utvecklingssteg är genomförda. Projektet är release-ready ur automatiserat CI-perspektiv; manuell Sparx EA-importverifiering kvarstår som extern gate.
