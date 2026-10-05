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
- ChatGPT Chat, ChatGPT Custom och OpenCode är fulla aktiva mål-runtimes.
- OpenAI Plugin är en aktiv `equivalent_runtime_dependent` peer runtime: samma canonical modell och tool-kontrakt, men full exekveringsparitet kräver persistent writable workspace och kompatibel code execution från hosten.
- Claude Projects är fortsatt reducerad/inaktiv.

## Nuvarande fas
Alla 19 utvecklingssteg är genomförda ur automatiserat projektperspektiv. OpenAI Plugin ingår nu som verifierad runtime-dependent peer distribution. Senaste maintenance-steget korrigerar Sparx MDG Technology-ID till högst 12 tecken efter praktisk importfeedback. Manuell Sparx EA-importverifiering ska köras om som extern gate.
