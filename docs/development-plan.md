# Utvecklingsplan – Metamodel Builder

## 1. Mål

Skapa en GPT som kan designa, skapa, underhålla, validera och versionshantera verktygsneutrala metamodeller, med Sparx Enterprise Architect MDG Technology som första fullständiga exportformat.

Den interna canonical-modellen ska vara verktygsneutral och lagras i YAML. Sparx EA-specifik implementation ska ligga i en separat adapter så att samma metamodell senare kan exporteras till andra arkitektur- och modelleringsverktyg.

## 2. Projektprofil

- Projektprofil: `zip_first_advanced`
- Modellrobusthet: `stateful`
- Primär sanningskälla: canonical YAML + strukturerad projektstatus
- Historik: Git
- Genererade artefakter ska aldrig vara canonical source
- Alla aktiverade runtimes ska härledas från samma canonical kontrakt

## 3. Runtime-mål

### Aktiverade i v1
- ChatGPT Chat
- ChatGPT Custom
- OpenCode

### Bedömda men inte fullständigt aktiverade i v1
- Claude Projects
- OpenAI Plugin

## 4. Övergripande arkitektur

```text
sources/
    ↓
importers/
    ↓
canonical metamodel
    ↓
validators
    ↓
platform adapters
    ↓
generators
    ↓
generated artifacts
```

Canonical modellen delas upp i:

```text
metamodel/
├── metamodel.yaml
├── properties.yaml
├── constraints.yaml
├── viewpoints.yaml
├── notation.yaml
├── provenance.yaml
└── version.yaml
```

Sparx EA-adaptern ligger separat:

```text
platforms/
└── sparx-ea/
    ├── mapping.yaml
    ├── stereotypes.yaml
    ├── tagged-values.yaml
    ├── diagrams.yaml
    ├── toolboxes.yaml
    ├── quick-linker.yaml
    └── shapescripts/
```

## 5. Utvecklingssteg

### Steg 1 – Projektskelett och canonical kontrakt

Skapa första kompletta projektstrukturen.

Leverabler:
- `gpt-project.yaml`
- `project-status.yaml`
- `PROJECT.md`
- `STATUS.md`
- `README.md`
- `docs/development-plan.md`
- canonical instruktion
- capability contract
- artifact contract
- workspace/state contract
- runtime-konfiguration
- schemas för canonical metamodell

Definition of done:
- projektet lintar
- schemas är syntaktiskt giltiga
- stateful-krav valideras
- komplett projekt-ZIP kan byggas

### Steg 2 – Canonical metamodell v1

Definiera YAML-formatet för:
- metadata
- elementtyper
- relationstyper
- arv/generalization
- properties
- enumerations
- kardinalitet
- constraints
- viewpoints
- notation
- provenance
- versionering

Leverabler:
- JSON Schema/YAML-schema
- exempelmetamodell
- schema-validerare

Definition of done:
- giltig exempelmodell accepteras
- kända ogiltiga modeller avvisas deterministiskt

### Steg 3 – Semantisk validator

Bygg regler som kontrollerar sådant som inte kan uttryckas tillräckligt i schema.

Exempel:
- unika ID:n
- alla referenser finns
- arvscykler saknas
- source/target-typer finns
- viewpoints refererar bara till definierade typer
- property- och enumreferenser är giltiga
- förbjudna eller motsägande constraints identifieras

Definition of done:
- testsvit med positiva och negativa fall
- maskinläsbar valideringsrapport

### Steg 4 – Sparx EA mapping-model

Definiera hur canonical begrepp översätts till Sparx EA.

Omfattning:
- UML metaclasses
- stereotypes
- stereotype inheritance
- tagged values
- diagrams
- toolbox pages
- Quick Linker
- Shape Scripts
- MDG metadata

Viktig princip:
- Sparx-specifik metadata får inte läcka in i canonical semantik annat än via explicit adapterreferens.

### Steg 5 – Första MDG-generatorn

Generera en fungerande MDG Technology från en enkel canonical metamodell.

Första testmodellen bör innehålla:
- Capability
- Application
- Platform
- Business Process
- några properties
- några relationstyper
- en diagramtyp
- en toolbox

Definition of done:
- deterministisk XML-generering
- XML är well-formed
- strukturella MDG-kontroller passerar
- samma input ger samma output

### Steg 6 – MDG-validering och testfixture

Inför djupare kontroll av genererad MDG.

Kontroller:
- referenser mellan profiler
- stereotype/metaclass-mappningar
- toolbox-referenser
- diagramprofil
- tagged values
- Quick Linker-konfiguration
- Shape Script-resurser

Om praktiskt möjligt skapas även en minimal verifieringsprocedur för import i Sparx EA som användaren kan köra.

### Steg 7 – Dokumentationsgenerator

Generera Markdown-dokumentation från canonical modellen.

Dokumentationen ska minst visa:
- metamodellöversikt
- elementtyper
- relationstyper
- properties
- constraints
- viewpoints
- provenance
- versionsinformation

MDG och dokumentation ska genereras från samma canonical version.

### Steg 8 – Import av befintlig Sparx MDG

Bygg reverse-engineering från MDG XML till en intermediate representation och därefter canonical YAML.

Mål:
- stereotypes
- metaclasses
- tagged values
- diagrams
- toolboxes
- Quick Linker där formatet tillåter
- Shape Scripts
- bevarad Sparx-specifik information som inte kan översättas fullt semantiskt

Importerade delar ska märkas med provenance och confidence/limitations när round-trip inte är exakt.

### Steg 9 – Metamodell-diff och versionshantering

Inför semantisk jämförelse mellan två canonical versioner.

Identifiera:
- tillagda objekt
- borttagna objekt
- namnändringar
- ändrade properties
- ändrade relationer
- ändrade constraints
- ändrade viewpoints
- potentiellt breaking changes

Generera:
- change log
- release notes
- migrationsnoteringar

### Steg 10 – Standard-/källbaserad anpassning

Inför arbetsflöde för att skapa egen metamodell utifrån:
- ArchiMate
- UML
- BPMN
- TOGAF-relaterat material
- annan användarlevererad metamodell

Arbetsflödet ska:
1. analysera källmaterial
2. skapa provenance
3. föreslå urval/specialisering
4. få användarens verksamhetsmässiga godkännande där det behövs
5. uppdatera canonical modellen
6. validera
7. generera målartefakter

Inga kompletta tredjepartsspecifikationer ska distribueras i projektet om licensen inte tydligt tillåter det.

### Steg 11 – Stateful arbetsflöde för underhåll

Inför explicit workspace-status.

Exempel:

```text
workspace/
├── metamodel/
├── platforms/
├── sources/
├── generated/
└── state/
    ├── workspace-state.yaml
    └── change-log.yaml
```

GPT:n ska kunna återuppta ett projekt från ZIP utan att chatthistoriken behövs.

### Steg 12 – ChatGPT Chat-distribution

Bygg portabel Chat ZIP med:
- instruktion
- schemas
- relevanta validators
- mallar
- runtime-kontrakt
- workspace-kontrakt

Verifiera återupptagning från befintligt metamodellprojekt.

### Steg 13 – ChatGPT Custom-distribution

Skapa Custom GPT-kompilation med:
- komprimerad men komplett instruktion
- nödvändiga Knowledge-filer
- tydligt filbaserat import/export-flöde

Dokumentera begränsningar relativt Chat-runtime.

### Steg 14 – OpenCode-distribution

Bygg OpenCode-runtime med stöd för:
- lokalt workspace
- filoperationer
- validators
- generators
- Git-baserat arbetsflöde

OpenCode bör vara den mest kompletta exekverbara utvecklingsmiljön för lokal MDG-utveckling.

### Steg 15 – Runtime parity och slutlig kvalitetssäkring

Verifiera att aktiverade runtimes följer samma:
- semantik
- canonical modell
- valideringsregler
- artefaktkontrakt
- versionsregler

Skillnader ska dokumenteras som plattformsbegränsningar, inte som olika GPT-beteenden.

### Steg 16 – Release pipeline

GitHub Actions:
- lint
- schema validation
- semantic tests
- generator tests
- project hygiene
- distribution build
- distribution validation

Release:
- versionsnummer från Git-tag
- full projekt-ZIP
- Chat ZIP
- Custom GPT ZIP
- OpenCode ZIP
- release notes

## 6. Prioritering

Följande måste fungera tidigt:

1. canonical YAML
2. deterministisk validering
3. Sparx EA mapping
4. enkel fungerande MDG-generator

Reverse engineering, standardimport och fler runtimes byggs först när exportkedjan är stabil.

## 7. Första vertikala testscenario

För att undvika att bygga för mycket infrastruktur innan något går att använda ska första fungerande end-to-end-testet vara:

```text
metamodel.yaml
   ↓
schema validation
   ↓
semantic validation
   ↓
Sparx mapping
   ↓
MDG XML
   ↓
MDG validation
```

Exempelmodellen ska innehålla ett litet men realistiskt arkitekturspråk med Capability, Application, Platform och Business Process.

## 8. Viktiga arkitekturprinciper

- Canonical YAML är sanningskällan.
- Genererad MDG XML redigeras aldrig som primär källa.
- Plattformsspecifika detaljer hålls i adapters.
- Importerade modeller behåller provenance.
- Alla generatorer ska vara deterministiska där det är möjligt.
- Validering sker före generering.
- Breaking changes identifieras på canonical nivå.
- Projektet ska kunna återupptas helt från ZIP.
- En framtida exporter för andra modelleringsverktyg ska kunna läggas till utan att canonical modellen designas om.

## 9. Nästa rekommenderade steg

Skapa projektskelettet och första canonical kontrakten enligt Steg 1. I samma steg ska den första kompletta projekt-ZIP:en byggas och valideras.

### Steg 17 – Modelleringshandledning och dokumentexport

Inför canonical `guidance.yaml` med användningsråd för element, relationer och viewpoints samt mönster, antimönster och FAQ. Generera Metamodel Reference, Modeling Guide och Quick Reference i Markdown, Confluence markup och PDF.

Definition of done:
- guidance schema och semantiska korsreferenser valideras
- Architecture Lite innehåller komplett exempelhandledning
- 3 dokumenttyper × 3 format genereras
- PDF renderas och verifieras
- runtimepaketen innehåller schema, exporter och relevant kunskap
