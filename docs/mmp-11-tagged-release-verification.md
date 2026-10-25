# Taggbunden slutverifiering av MMP 1.1-kandidaten

Den manuella GitHub Actions-körningen `MMP 1.1 tagged candidate verification` kan endast slutföras när användaren uttryckligen väljer en **existerande tagg** som workflow-ref. Den skapar inte taggar och publicerar inte releaser.

Verifieringen kontrollerar:
- Projektets befintliga regressioner (inklusive MMP 1.0).
- Python- och TypeScript-tester för kandidaternas deklarerade profiler samt ett kombinerat paket.
- Deterministiskt Specification Kit **1.2.0**, med paketformat **1.1.0**, byggt från vald commit.
- SHA-256 för exakt den ZIP-artefakt som byggdes och en oberoende byteidentisk ombyggnad från samma checkout.
- Fullständig inventering i ZIP-paketets `SHA256SUMS.txt`.

En rapport `mmp11-release-evidence.json`, ZIP och kontrollsumma sparas som **workflow artifact**, inte som GitHub Release asset. Befintligt Specification Kit 1.1.0 för MMP 1.0 ändras inte.

**Beslut:** Grön verifiering är ett nödvändigt evidensunderlag, inte ett automatiskt GO. Manuell granskning av scope, tagg och releasebeslut återstår. Publiceringsflödet i den äldre `release.yml` ändras inte och är inte del av denna verifiering. Använd därför inte den äldre publiceringsrutinen som ersättning för den taggbundna grinden.
