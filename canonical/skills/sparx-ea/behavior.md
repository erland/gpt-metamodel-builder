# Sparx Enterprise Architect / MDG

## Aktivering
När användaren vill importera Sparx EA MDG, utveckla adapter/mapping, generera MDG eller kontrollera Sparx-kompatibilitet.

## Beteende
- Håll Sparx-specifika begrepp strikt i adapter: UML metaclasses, stereotypes, tagged values, diagramprofiler, toolbox-profiler, Quick Linker, Shape Scripts och MDG-metadata.
- Importera MDG med `scripts/import_sparx_mdg.py` när möjligt. Redovisa provenance, approximationer och förlorad designintention vid reverse engineering.
- Validera Sparx-mapping med `scripts/validate_sparx_mapping.py` före generering.
- Generera MDG med `scripts/generate_sparx_mdg.py` och validera med `scripts/validate_generated_mdg.py` där miljön stöder det.
- `technology.id` ska vara unikt och högst 12 tecken. Använd ett stabilt kort adapter-ID, medan det mänskligt läsbara namnet finns i `technology.name`.
- MDG XML är en genererad artefakt, inte canonical source; samma canonical input ska ge deterministiskt resultat.
- Manuell import i riktig Sparx EA är en separat extern verifieringsgate och får aldrig rapporteras som PASS utan faktisk import.
