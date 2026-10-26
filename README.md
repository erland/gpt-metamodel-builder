# Metamodel Builder

Metamodel Builder är ett GPT-projekt för att **skapa, underhålla, validera och distribuera verktygsneutrala metamodeller**. Modellen lagras i canonical YAML och kan användas som underlag för dokumentation, utbytespaket och verktygsspecifika projektioner. Sparx Enterprise Architect MDG Technology är den första fullständiga målplattformen.

Projektets generella utbytesformat är **Metamodel Exchange Package (MMP)**. Nya exporter använder **MMP 1.1.0** som standard; **MMP 1.0.0** stöds fortsatt vid uttryckligt kompatibilitetsval. **MMP Specification Kit** har en separat versionsnumrering. MMP är ett projektspecifikt format, inte en extern standard.

## Kom igång

Välj den väg som passar användningen:

- **Arbeta med en metamodell:** använd en av Metamodel Builders runtime-distributioner från [GitHub Releases](https://github.com/erland/gpt-metamodel-builder/releases). Canonical YAML är alltid sanningskällan.
- **Utbyta en metamodell med andra verktyg:** exportera ett MMP-paket och låt en konsument inspektera, validera eller importera det i en ny arbetsyta. Se [MMP-formatkontraktet](docs/mmp-v1-contract.md).
- **Skapa en Sparx EA MDG:** använd adaptern i `platforms/sparx-ea/`. Genererad MDG XML är en artefakt, inte primär modellkälla; riktig import i Enterprise Architect måste verifieras separat.
- **Utveckla projektet:** börja med `gpt-project.yaml`, `project-status.yaml` och [utvecklingsplanen](docs/development-plan.md).

### Exempel: exportera och läsa MMP

Validera först canonical modell enligt dess scheman och semantiska regler. Modellen måste ha en **stabil URI-namnrymd** i `metamodel.yaml`.

```bash
python scripts/export_mmp.py --model-dir /path/to/model --output model.mmp.zip --producer-version "$PRODUCENTVERSION"
python scripts/import_mmp.py inspect model.mmp.zip
python scripts/import_mmp.py validate model.mmp.zip
python scripts/import_mmp.py import model.mmp.zip --output /path/to/new-model
python interop/mmp_v1_consumer.py model.mmp.zip
```

Sätt miljövariabeln `PRODUCENTVERSION` till den faktiska versionen av Metamodel Builder som producerar paketet innan kommandot körs. Importören skriver aldrig över en befintlig destination. Exportören stöder även katalogformat med `--directory`.

## Grundprinciper och funktioner

**Canonical YAML är sanningskällan.** Modellens element, relationer, egenskaper och övriga definitioner underhålls i YAML och valideras mot JSON Schemas samt semantiska regler.

- **Versionsjämförelse:** `scripts/diff_metamodel.py` jämför canonical modeller, bedömer kompatibilitet och kan generera diff, releaseanteckningar och migrationsnoteringar.
- **Modelleringshandledning:** `guidance.yaml` beskriver när element, relationer och viewpoints ska användas.
- **Dokumentexport:** `scripts/export_documentation.py` kan generera Metamodel Reference, Modeling Guide och Quick Reference i Markdown, Confluence markup och PDF.
- **Sparx EA:** `platforms/sparx-ea/` innehåller adaptern. Deterministisk MDG-validering kompletteras av ett manuellt importtest i `tests/sparx-ea/manual-import-fixture.yaml`.

## Distributioner

Metamodel Builder använder den versionslåsta distributionsmotorn **GPT Byggaren 1.6.33**. Releaseflödet bygger ett projektpaket samt fem runtime-distributioner:

| Distribution | Användning |
| --- | --- |
| Chat | Användning via projektpaket i chattmiljö |
| OpenAI Plugin | Skills-first-distribution i ChatGPT |
| Claude Project | Projektmiljö i Claude |
| Claude Skills | Skill-baserad användning i Claude |
| OpenCode | Runtime för OpenCode |

Därutöver skapas en **domänmotor**, `metamodel-builder-engine-<VERSION>.zip`, och **MMP Specification Kit**. Någon Custom GPT-distribution byggs inte längre.

Skripten ingår i runtime-distributionernas Skill-resurser. Kör dem där värdmiljön erbjuder kompatibel Python och nödvändiga projektresurser. I ChatGPT Plugins chattläge kan den versionsmatchade Engine ZIP-filen från samma GitHub-release behövas när direkt körning av Skill-skript inte är möjlig.

OpenAI Plugin är en skills-first `equivalent_runtime_dependent` peer runtime. Full deterministisk runtimeparitet kräver bland annat en skrivbar arbetsyta och kompatibel kodexekvering; en grön byggkontroll bevisar inte funktionalitet i varje värdmiljö.

## MMP – generellt metamodellutbyte

**MMP-format 1.0.0** är det äldre deklarativa, verktygsneutrala utbytesformatet för **metamodeller**. Paketet består av sju obligatoriska canonical YAML-resurser, valfri `guidance.yaml`, lokala JSON Schemas samt manifest med SHA-256-kontrollsummor. Det innehåller **inte** modellinstanser, Sparx-konfiguration, exekverbar kod eller Engine ZIP.

**MMP Specification Kit 1.1.0** är en **enda separat distributions-ZIP**, `mmp-specification-kit-1.1.0.zip`, med formatkontrakt, schemas, exempelpaket, referenskonsument, testfall och dokumentation. Kit-versionen beskriver utgåvan av materialet och är **inte samma sak** som MMP-paketets formatversion. Versionskällan är `mmp-kit/version.json`.

Frivilliga kandidater som **Strict Core**, kanonisk värdesemantik och extensionförhandling är ännu inte fullständigt normativa eller verifierade som MMP Core 1.1.0. De förändrar inte implicit valideringen av MMP 1.0.0.

Läs vidare i [formatkontraktet](docs/mmp-v1-contract.md), [versionsbeslutet](docs/mmp-version-compatibility-decision.md) och [releaseacceptansen](docs/mmp-release-acceptance.md). Kit-innehållet beskrivs i [mmp-kit/README.md](mmp-kit/README.md).

## Utveckling och tester

Projektets centrala ingångar är:

| Sökväg | Innehåll |
| --- | --- |
| `gpt-project.yaml` | Projekt- och runtimekontrakt |
| `project-status.yaml` | Utvecklingsstatus |
| `canonical/core.md`, `canonical/skills/*/behavior.md` | Aktuellt canonical GPT-beteende |
| `assistant/instructions.md` | Historiskt migrationsunderlag |
| `metamodel/`, `schemas/` | Modellfiler och JSON Schemas |
| `platforms/sparx-ea/` | Sparx EA-adapter |
| `evals/model-compatibility/` | Robusthetsfall |

Kör projektets regressionssvit med lämpliga Python-beroenden installerade:

```bash
python scripts/run_ci.py --project-root .
```

CI kontrollerar bland annat canonical schema/semantik, Sparx-mappning, MMP-manifest, säker import/export, interoperabilitet och delar av konformitetsprofilerna. TypeScript-konsumenten verifieras separat i `.github/workflows/mmp-typescript.yml`. Testresultat ersätter inte praktisk körning i Plugin, Claude, OpenCode eller Sparx EA.

## Release och versioner

Vid publicering av en GitHub-release med tagg `v<VERSION>` använder `.github/workflows/release.yml` **GPT Byggaren 1.6.33** för att bygga och verifiera Metamodel Builders distributioner. Flödet bygger också det versionsstyrda MMP Specification Kit, kontrollerar paketinnehåll och lägger till ZIP-filen och SHA-256-kontrollsummor bland releaseartefakterna.

**Tre olika versioner förekommer och ska inte blandas ihop:**

| Version | Vad den beskriver |
| --- | --- |
| Metamodel Builder `<VERSION>` | Releaseversion för projektets runtime-distributioner och Engine ZIP |
| MMP `1.0.0` | Stabilt utbytesformat och manifestkontrakt |
| MMP Specification Kit `1.1.0` | Utgåva av specifikation, exempel och testmaterial |

Integritetsunderlag finns i `DELIVERY-MANIFEST.json` och `SHA256SUMS.txt`. En separat kontrollsummefil för MMP-kitet är **inte** ett andra distributionspaket. Se [releasechecklistan](docs/mmp-v1-release-checklist.md) för kvarstående praktiska acceptansmoment.

---
Metamodel Builder utvecklas för att en canonical metamodell ska kunna **återanvändas i flera verktyg** utan att bindas till en enskild modelleringsplattform.

## Migrering av befintliga MMP 1.0-paket

Standardexporten använder MMP 1.1. MMP 1.0 kräver flaggan `--legacy-1-0`. För att konvertera ett befintligt validerat paket utan att ändra den ursprungliga canonical-semantiken:

```bash
python scripts/migrate_mmp.py old.mmp.zip --output new.mmp.zip --report migration.json
```

Kommandot kontrollerar manifest, SHA-256, källans scheman och semantik, bygger en MMP 1.1-fil samt validerar och återimporterar den. Det vägrar skriva över befintliga filer och skapar en JSON-rapport. Originalets canonical-filer bevaras byte-för-byte; om äldre paket saknar valfri `guidance.yaml` anges eventuell tillagd mallfil separat i rapporten. Kommandot hittar **inte på** nya MMP 1.1-relationer, typade ändpunkter eller junction-regler. Sådana ändringar måste göras som en separat, avsiktlig semantisk uppgradering.
