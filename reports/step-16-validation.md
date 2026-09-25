# Steg 16 – valideringsrapport

## Resultat

**PASS** – release pipeline är implementerad och lokalt verifierad.

## Implementerat

- `.github/workflows/ci.yml`
  - push till `main`
  - pull requests
  - manuell körning
  - full regressionsvit
  - distributionsbygge
  - distributionsvalidering
  - workflow artifact
- `.github/workflows/release.yml`
  - publicerad GitHub Release
  - manuell verifierad release-build
  - version från `github.event.release.tag_name` vid Release-event
  - full regressionsvit
  - distributionsbygge och validering
  - `gh release upload --clobber`
- `scripts/run_ci.py`
- `scripts/build_distributions.py`
- `scripts/validate_distributions.py`
- `scripts/build_release.py`
- `scripts/validate_chat_runtime.py`
- `docs/release-pipeline-v1.md`

## Automatiska gates

Följande har verifierats i denna miljö:

- project foundation contract: PASS
- model robustness: PASS
- canonical schemas: PASS
- semantic validation regression: PASS
- Sparx mapping regression: PASS
- MDG generator regression: PASS
- MDG validation regression: PASS
- documentation generator regression: PASS
- Sparx MDG importer regression: PASS
- metamodel diff/versioning regression: PASS
- source adaptation regression: PASS
- workspace resume regression: PASS
- project lint: PASS, 0 fel och 0 varningar
- project hygiene: PASS
- Chat runtime validation: PASS
- Custom GPT runtime validation: PASS
- OpenCode runtime validation: PASS
- runtime parity: PASS
- release manifest/checksums: PASS

Den sammanhållna `run_ci.py`-körningen träffade den lokala exekveringsmiljöns kommandotidsgräns efter fem passerade gates. Resterande gates kördes därför separat och passerade. GitHub Actions använder samma `run_ci.py` utan denna konversationsmiljös korta kommandotidsgräns.

## Determinism

Två oberoende byggen av `0.1.0-dev.16` gav identiska SHA-256 för:

- canonical project ZIP
- ChatGPT Chat ZIP
- ChatGPT Custom ZIP
- OpenCode ZIP

## Kvarstående extern gate

Manuell importverifiering i Sparx Enterprise Architect är definierad i `tests/sparx-ea/manual-import-fixture.yaml`, men Enterprise Architect finns inte i denna miljö. Den kontrollen är därför uttryckligen **inte markerad som genomförd** och ska göras inför/vid första produktionsrelease när EA finns tillgängligt.
