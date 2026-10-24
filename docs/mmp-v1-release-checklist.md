# Releasegranskning – MMP v1

Status per 2026-10-24: **automatiserade releasekontroller PASS**, oberoende runtime-acceptans **PARTIAL**. Skapa ingen ny version enbart utifrån den här checklistan utan godkänd releaseprocess.

## Automatiska kontroller

- [x] Canonical schema/semantik, Sparx och workspace regression i `scripts/run_ci.py`.
- [x] MMP manifest, ZIP/export, import/roundtrip, manipulationsskydd, oberoende referenskonsument och identitetsutveckling.
- [x] Faktiskt genererade Plugin-, Claude Skills- och Engine-arkiv har verifierats i preflight efter PR #22 med `scripts/test_mmp_distribution_archives.py`.
- [x] Domän-Engine har utökad självtestsvit med MMP-fallen och SHA-256-inventering.
- [x] Releaseworkflow kör motsvarande kontroller och publicerar distributionsartefakter vid `release: published`.

## Återstående acceptans (blockerar påståenden om *fullständig* runtimeparitet)

- [ ] Verklig funktionell export/import i installerad Plugin i ny chatt, med versionsmatchad publicerad Engine som reservväg.
- [ ] Direkt körning av MMP-skript i Claude Skills och OpenCode på faktiska värdar.
- [ ] Externt verktyg har läst MMP v1 utan projektets Pythonreferenskonsument.
- [ ] Praktisk Sparx Enterprise Architect-import av genererad MDG, om Sparx-kompatibilitet ska hävdas för releasen.
- [ ] Återstående semantiska MMP-kriterier 4, 5 och 7 är dokumenterade som PARTIAL i `docs/mmp-v1-acceptance-status.md`.

## Releaseförfarande

1. Merga releaseförberedande ändringar när de båda PR-kontrollerna är gröna.
2. Säkerställ att en **ny, vald version** är större än den publicerade 1.2.2-versionen (t.ex. välj 1.3.0 enligt projektets versionspolicy); detta dokument skapar inte en release.
3. Skapa och publicera GitHub Release med tagg `v<VERSION>`. Release-workflow bygger artefakter mot exakt samma version.
4. Kontrollera sex distributionsarkiv, separat `metamodel-builder-engine-<VERSION>.zip`, `DELIVERY-MANIFEST.json`, `SHA256SUMS.txt` och publicerad direktlänk till Engine ZIP.
5. Kör den versionsmatchade Engine ZIP-filens riktiga `scripts/selftest_metamodel_engine.py` och kontrollera rapportens individuella exitkoder.
6. Testa installerad Plugin i en **ny** konversation med en ny canonical metamodell: exportera MMP, validera med oberoende konsument, importera i ny arbetsyta och jämför identifierare, relationer och egenskaper.
7. Sätt runtimeacceptans till PASS endast för miljöer som verkligen körts. Dokumentera negativa/ej körda kontroller som PARTIAL respektive NOT TESTED.

## Princip

De paketerade Skill-skripten är alltid förstahandsväg. Engine ZIP begärs **endast** om värdens exekvering av paketerade skript saknas. MMP ZIP är en deklarativ utbytesfil, inte en Engine. Självtest och distribuerade ZIP-kontroller ersätter inte ett externt värdmiljötest.
