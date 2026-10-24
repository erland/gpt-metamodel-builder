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

OpenAI Plugin distribueras som en skills-first `equivalent_runtime_dependent` peer runtime. Canonical instruktion, workflow-policy, schemas, metamodell, Sparx-adapter, templates, workspace och de 11 verkliga modell-/generatorverktygen följer med som skill-resurser. Pluginen skapar ingen MCP-wrapper enbart för scriptkörning. Full deterministisk parity kräver persistent writable workspace och kompatibel Python/code execution; faktisk Sparx EA-import förblir en extern manuell verifieringsgate.

## Distribution och release (GPT Byggaren 1.6.31)

Canonical beteende finns i `canonical/core.md` och fyra avgränsade `canonical/skills/*/behavior.md`. `assistant/instructions.md` är historisk källa för migrationsspårbarhet.

Originalmotorn GPT Byggaren 1.6.31 skapar ett projektpaket och fem distributioner: Chat, OpenAI Plugin, Claude Projects, Claude Skills och OpenCode. CI kör domänregressionstesterna separat; `.github/workflows/gpt-byggaren-engine.yml` verifierar engine-build, medan `.github/workflows/release.yml` använder samma versionslåsta motor för release. Custom GPT byggs inte längre.

Releasepaketens integritet styrks av `DELIVERY-MANIFEST.json` och `SHA256SUMS.txt`. Runtimeparitet kräver fortfarande separat funktionell verifiering i respektive värdmiljö. Manuell Sparx EA-import är inte automatiskt verifierad.
