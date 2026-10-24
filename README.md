# Metamodel Builder

Metamodel Builder är ett GPT-projekt för att skapa och underhålla verktygsneutrala metamodeller. Canonical data lagras i YAML och kan senare projiceras till olika modelleringsverktyg. Första fullständiga målplattformen är Sparx Enterprise Architect MDG Technology.

## Viktiga filer
- `gpt-project.yaml` – projekt- och runtimekontrakt
- `project-status.yaml` – auktoritativ utvecklingsstatus
- `assistant/instructions.md` – canonical GPT-instruktion
- `docs/development-plan.md` – persistent utvecklingsplan
- `schemas/metamodel.schema.json` – första canonical grundschema
- `metamodel/` – canonical metamodellfiler
- `platforms/sparx-ea/` – Sparx EA-adapter
- `evals/model-compatibility/` – robusthetsfall

## Princip
Canonical YAML är sanningskällan. Genererad MDG XML är en artefakt och redigeras inte som primär källa.

## Sparx EA verifiering

Den genererade MDG:n valideras deterministiskt. För faktisk produktverifiering i Enterprise Architect finns `tests/sparx-ea/manual-import-fixture.yaml`.

## Versionshantering

`scripts/diff_metamodel.py` jämför två canonical modeller semantiskt, klassar kompatibilitet och kan generera JSON-diff, release notes och migrationsnoteringar.

## Modelleringshandledning och dokumentexport

Canonical `guidance.yaml` beskriver när element, relationer och viewpoints ska användas. `scripts/export_documentation.py` kan generera Metamodel Reference, Modeling Guide och Quick Reference i Markdown, Confluence markup och PDF.


## OpenAI Plugin

OpenAI Plugin distribueras som en skills-first `equivalent_runtime_dependent` peer runtime. Canonical instruktion, workflow-policy, schemas, metamodell, Sparx-adapter, templates, workspace och de deklarerade modell-/generatorverktygen och MMP-export/import följer med som Skill-resurser. Pluginen skapar ingen MCP-wrapper enbart för scriptkörning. Full deterministisk parity kräver persistent writable workspace och kompatibel Python/code execution; faktisk Sparx EA-import förblir en extern manuell verifieringsgate.

## Distribution och release (GPT Byggaren 1.6.32)

Canonical beteende finns i `canonical/core.md` och fyra avgränsade `canonical/skills/*/behavior.md`. `assistant/instructions.md` är historisk källa för migrationsspårbarhet.

Originalmotorn GPT Byggaren 1.6.32 skapar ett projektpaket och fem distributioner: Chat, OpenAI Plugin, Claude Projects, Claude Skills och OpenCode. CI kör domänregressionstesterna separat; `.github/workflows/gpt-byggaren-engine.yml` verifierar engine-build, medan `.github/workflows/release.yml` använder samma versionslåsta motor för release. Custom GPT byggs inte längre.

Releasepaketens integritet styrks av `DELIVERY-MANIFEST.json` och `SHA256SUMS.txt`. Runtimeparitet kräver fortfarande separat funktionell verifiering i respektive värdmiljö. Manuell Sparx EA-import är inte automatiskt verifierad.

## Separat domänmotor (Engine ZIP)

Utöver projekt-ZIP och fem runtimepaket byggs `metamodel-builder-engine-<version>.zip`. **Skripten finns kvar i runtimedistributionernas Skills.** Kör dem direkt när värdmiljön erbjuder kompatibel Python och tillhörande projektresurser. I ChatGPT Plugins chattläge, där direkt exekvering av Skill-skript inte är tillgänglig, kan användaren i stället bifoga den versionsmatchade Engine ZIP-filen från samma GitHub Release.

Engine ZIP innehåller domänskript, schemas, mallar, exempelfiler, tester och workspace-underlag och har en maskinläsbar `engine-package.json` med SHA-256 per fil. Efter uppackning kan dess verkliga självtest köras med `python scripts/selftest_metamodel_engine.py` (kräver Python med PyYAML, jsonschema och reportlab). Självtestet omfattar canonical schema, semantik, Sparx-mappning/MDG, workspace-återupptagning samt MMP v1:s manifest, export/import, säkerhet, interoperabilitet och identitetstester. Ingen lokal Sparx Enterprise Architect-installation ingår; en verklig EA-import förblir manuell.

## MMP v1 – generellt metamodellutbyte

MMP (`Metamodel Exchange Package`) är ett föreslaget, verktygsneutralt utbytesformat för metamodeller – **inte** en extern standard. Canonical YAML förblir sanningskällan. Exporten innehåller sju obligatoriska canonical YAML-filer, valfri `guidance.yaml`, offline JSON Schemas och SHA-256-verifierade manifestposter. MMP innehåller inte modellinstanser eller Sparx-konfiguration.

Exportera först efter godkänd schema- och semantikvalidering och med en stabil URI-namnrymd i `metamodel.yaml`:

```bash
python scripts/export_mmp.py --model-dir /path/to/model --output model.mmp.zip --producer-version 1.2.2
python scripts/import_mmp.py inspect model.mmp.zip
python scripts/import_mmp.py validate model.mmp.zip
python scripts/import_mmp.py import model.mmp.zip --output /path/to/new-model
python interop/mmp_v1_consumer.py model.mmp.zip
```

Vid import skrivs **aldrig** en befintlig destination över. Samma paket kan exporteras som katalog med `--directory`. `--producer-version` är den byggda producentens verkliga version; ersätt exempelvärdet ovan för ny release. Formatkontraktet finns i [docs/mmp-v1-contract.md](docs/mmp-v1-contract.md), och evidensbaserade acceptansbegränsningar i [docs/mmp-v1-acceptance-status.md](docs/mmp-v1-acceptance-status.md).

**Releaseberedskap:** GitHub CI och distributionsarkivkontroller är godkända; live-exekvering i installerade Plugin/Claude/OpenCode och externa konsumentverktyg måste prövas separat. Se [docs/mmp-v1-release-checklist.md](docs/mmp-v1-release-checklist.md).
