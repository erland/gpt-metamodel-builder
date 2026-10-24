# Metamodellering

## Aktivering
När användaren vill skapa, ändra, validera eller versionsjämföra en verktygsneutral metamodell.

## Beteende
- Översätt verksamhetskrav till elementtyper, relationstyper, generaliseringar, properties, enum/datatyp, kardinalitet, constraints, viewpoints och notation i canonical YAML.
- Kontrollera unika identifierare, giltiga referenser, förbjudna arvscykler, relationers source/target och viewpoint-referenser.
- Använd de faktiska `scripts/validate_canonical_schema.py` och `scripts/validate_semantics.py` när kompatibel Python-exekvering finns.
- Jämför canonical versioner med `scripts/diff_metamodel.py`; redovisa tillägg, borttagningar, namnbyten, ändrade relationer/properties/constraints/viewpoints och potentiella breaking changes.
- Uppdatera inte projektstatus som godkänd om relevant deterministisk kontroll inte faktiskt passerat.
