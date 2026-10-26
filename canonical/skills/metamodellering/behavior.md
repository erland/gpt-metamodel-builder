# Metamodellering

## Aktivering
När användaren vill skapa, ändra, validera eller versionsjämföra en verktygsneutral metamodell.

## Beteende
- Översätt verksamhetskrav till elementtyper, relationstyper, generaliseringar, properties, enum/datatyp, kardinalitet, constraints, viewpoints och notation i canonical YAML.
- Kontrollera unika identifierare, giltiga referenser, förbjudna arvscykler, relationers source/target och viewpoint-referenser.
- Använd de faktiska `scripts/validate_canonical_schema.py` och `scripts/validate_semantics.py` när kompatibel Python-exekvering finns.
- Jämför canonical versioner med `scripts/diff_metamodel.py`; redovisa tillägg, borttagningar, namnbyten, ändrade relationer/properties/constraints/viewpoints och potentiella breaking changes.
- Uppdatera inte projektstatus som godkänd om relevant deterministisk kontroll inte faktiskt passerat.

## MMP-standard för nya modeller
- Nya metamodeller ska utgå från **MMP 1.1** som standard. Modellera typade source/target-referenser, exakta tillåtna relationspar och junctions när det behövs; reducera inte modellen till MMP 1.0:s begränsningar.
- Deklarera nödvändiga MMP 1.1-kapabiliteter i canonical metadata. Bär bara kapabiliteter som faktiskt används och kan hanteras av mottagaren.
- MMP 1.0 är ett uttryckligt äldre kompatibilitetsval, aldrig startpunkt eller tyst fallback. Fråga bara efter 1.0 om användaren kräver äldre utbyte.

## MMP-export
- Exportera en godkänd canonical metamodell i **MMP 1.1** med `scripts/export_mmp.py` när användaren efterfrågar utbyte med andra verktyg.
- Kräv en stabil, godkänd URI-namespace och fullständig schema-/semantikvalidering före export.
- Behåll käll-YAML oförändrad och inkludera checksummor samt lokalt användbara JSON Schemas. Använd inbyggt skript när det går att exekvera; separat versionsmatchad Engine ZIP endast som reservväg.
- Skilj MMP (deklarativ utbytesfil) från körbara Engine ZIP och målverktygsspecifik Sparx MDG.

## MMP-import
- Importera verktygsneutrala MMP 1.1-paket (och äldre 1.0-paket när sådana uttryckligen förekommer) med `scripts/import_mmp.py` i lägena `inspect`, `validate` och `import`.
- Kontrollera ZIP-säkerhet, manifest, SHA-256 och medföljande JSON Schemas innan canonical semantik verifieras.
- Skriv aldrig över existerande projekt; importera i en ny användarvald katalog och behåll originalpaketet oförändrat.
- Kör paketerade skript direkt där de kan exekveras; begär versionsmatchad Engine ZIP enbart som reservväg.

## Migrering från MMP 1.0 till 1.1
- Känn igen MMP 1.0 och erbjud förlustfri formatmigrering med `scripts/migrate_mmp.py`.
- Validera källa och mål, återimportera och jämför originalets canonical-filer byte för byte. Behåll originalfilen orörd och skriv aldrig över befintliga mål.
- Redovisa tillagd `guidance.yaml` separat när äldre paket saknade den frivilliga filen.
- Skapa en maskinläsbar migrationsrapport. Markera inte användarvalda utökningar som automatiskt migrerade.
- Erbjud separat semantisk uppgradering av typade par, ändpunkter och junction-regler med explicit användarbeslut och validering. Härled aldrig sådan semantik automatiskt från bara ett 1.0-paket.
