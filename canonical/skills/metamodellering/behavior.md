# Metamodellering

## Aktivering
När användaren vill skapa, ändra, validera eller versionsjämföra en verktygsneutral metamodell.

## Beteende
- Översätt verksamhetskrav till elementtyper, relationstyper, generaliseringar, properties, enum/datatyp, kardinalitet, constraints, viewpoints och notation i canonical YAML.
- Kontrollera unika identifierare, giltiga referenser, förbjudna arvscykler, relationers source/target och viewpoint-referenser.
- Använd de faktiska `scripts/validate_canonical_schema.py` och `scripts/validate_semantics.py` när kompatibel Python-exekvering finns.
- Jämför canonical versioner med `scripts/diff_metamodel.py`; redovisa tillägg, borttagningar, namnbyten, ändrade relationer/properties/constraints/viewpoints och potentiella breaking changes.
- Uppdatera inte projektstatus som godkänd om relevant deterministisk kontroll inte faktiskt passerat.

## MMP-export
- Exportera en godkänd canonical metamodell i generellt MMP v1-format med `scripts/export_mmp.py` när användaren efterfrågar utbyte med andra verktyg.
- Kräv en stabil, godkänd URI-namespace och fullständig schema-/semantikvalidering före export.
- Behåll käll-YAML oförändrad och inkludera checksummor samt lokalt användbara JSON Schemas. Använd inbyggt skript när det går att exekvera; separat versionsmatchad Engine ZIP endast som reservväg.
- Skilj MMP (deklarativ utbytesfil) från körbara Engine ZIP och målverktygsspecifik Sparx MDG.

## MMP-import
- Importera verktygsneutrala MMP v1-paket med `scripts/import_mmp.py` i lägena `inspect`, `validate` och `import`.
- Kontrollera ZIP-säkerhet, manifest, SHA-256 och medföljande JSON Schemas innan canonical semantik verifieras.
- Skriv aldrig över existerande projekt; importera i en ny användarvald katalog och behåll originalpaketet oförändrat.
- Kör paketerade skript direkt där de kan exekveras; begär versionsmatchad Engine ZIP enbart som reservväg.
