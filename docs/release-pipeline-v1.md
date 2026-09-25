# Release pipeline v1

Metamodel Builder har två GitHub Actions-flöden.

## CI

`.github/workflows/ci.yml` körs på push till `main`, pull request och manuellt. Den:

1. installerar Python, PyYAML, jsonschema och ReportLab,
2. kör `scripts/run_ci.py`,
3. bygger Chat, Custom GPT och OpenCode med ett CI-versionsnummer,
4. validerar varje runtime och runtime parity,
5. laddar upp hela `dist/` som workflow artifact.

## Release

`.github/workflows/release.yml` körs när en GitHub Release publiceras och kan även startas manuellt för att skapa ett verifierat release-build utan att ladda upp till en Release.

Vid en publicerad release med taggen exempelvis `v0.1.0` används `0.1.0` som versionsnummer och följande byggs:

- canonical projekt-ZIP,
- ChatGPT Chat-ZIP,
- ChatGPT Custom-ZIP,
- OpenCode-ZIP,
- runtime parity-rapport,
- release manifest,
- SHA-256 checksummor.

Efter godkänd full validering laddas artefakterna upp till den redan publicerade GitHub Release-posten med `gh release upload --clobber`.

## Lokal reproduktion

```bash
python -m pip install PyYAML jsonschema reportlab
python scripts/run_ci.py --project-root .
python scripts/build_distributions.py --project-root . --output-dir dist --version 0.1.0
python scripts/validate_distributions.py --project-root . --output-dir dist --version 0.1.0
```

## Release gate

Automatiska gates måste vara gröna. Dessutom kvarstår den manuella Sparx EA-importverifieringen som en uttrycklig releasekontroll när en faktisk EA-miljö finns tillgänglig. CI får inte beskriva denna manuella kontroll som genomförd.
