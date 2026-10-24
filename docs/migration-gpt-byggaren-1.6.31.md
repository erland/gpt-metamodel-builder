# Migration till GPT Byggaren 1.6.31

Status: **påbörjad – inventering genomförd, fullständig migrering återstår**.

## 1. Inventering

Utgångspunkt är `main` i `erland/gpt-metamodel-builder`, kontrollerad 2026-10-24.

- Befintlig projektkonfiguration: `gpt-project.yaml`, `project-status.yaml`.
- Canonical beteende: `assistant/instructions.md` och `assistant/policies/workflow.md`.
- Verktygsneutral canonical metamodell i YAML och separat `platforms/sparx-ea/`-adapter.
- 11 produktverktyg i `scripts/` definierade i `tools.tools`; dessa ska bevaras.
- 19 historiska utvecklingssteg är avslutade och får inte markeras som ej genomförda.
- Aktiva distributionsmål: Chat, Custom GPT, OpenCode och Plugin. Claude Projects är inaktiv.
- CI/release använder projektlokala scripts. Ingen ersättning får ske förrän funktionsparitet är belagd.
- Manuell importkontroll i Sparx EA är fortfarande en extern, **icke verifierad** gate.
- Dokumentationen motsäger delvis faktisk status (exempelvis v1-planens runtime-lista).

## 2. Mål och migrationsbeslut

Målversion: **GPT Byggaren engine 1.6.31**. Projektets eget versionsnummer ändras inte av detta.

- Fem mål: `chat`, `plugin`, `claude_project`, `claude_skills`, `opencode`.
- Historisk `custom_gpt` tas bort från aktiva mål och byggkedja.
- Peer-runtimes härleds från samma beteende-, capability-, artifact-, state- och tool-kontrakt.
- Rekommenderad modulär instruktion:
  - `canonical/core.md`: sanningskälla, semantisk säkerhet, status, valideringsgates, provenance och genereringsordning.
  - `canonical/skills/metamodellering/behavior.md`: skapa, redigera och jämföra canonical metamodell.
  - `canonical/skills/kallanpassning/behavior.md`: tolka externa standarder och godkänna adaptationsplaner.
  - `canonical/skills/sparx-ea/behavior.md`: import, mapping, MDG-generering och extern EA-gate.
  - `canonical/skills/dokumentation/behavior.md`: modelleringshandledning och export.
- Slutlig uppdelning beslutas först efter spårbar kontroll av samtliga originalinstruktioner och resursberoenden; undvik duplicerade canonical regler.
- Varje Skill ska deklarera endast relevanta `references`, `assets`, `scripts` (och `skills.resource_policy: explicit` först efter genomförd resursinventering).
- Håll projektets domänvalidatorer och generatorer åtskilda från GPT Byggarens distributionsmotor.

## 3. Motor

- Använd officiell, versionslåst motor från `v1.6.31`, inte `main` eller `latest`.
- Bevara motorns ursprungliga installerare, builder och validatorer.
- Installations-/buildkontrakt anpassas till projektet utan att ersätta produktens domänskript.
- Den användarbifogade `gpt-byggaren-engine-1.6.31(1).zip` har kontrollerats separat: motorns original-`selftest_distribution_engine.py --source .` rapporterade godkänt SHA-256-steg, installerare och smoke build med sex arkiv. **Detta verifierar motorn, inte migrerad projektdistribution.**

## 4. Distributioner och tester

- Generera projekt-ZIP samt samtliga fem peer-distributioner från installerad originalmotor.
- Kontrollera projektunik `gpt-project.yaml`, modulära Skills och resurslistor.
- Jämför de 11 verkliga verktygen och deras runtime-krav mot respektive distribution.
- Kör canonical schema- och semantiska tester, MDG-generator/validator, versionsdiff, källanpassning, dokumentexport och workspace-återupptagning.
- Kör motorns `lint_gpt_project.py`, `validate_generated_delivery.py`, `validate_distributions.py`, `validate_portable_skills.py` samt projektspecifika CI-tester.
- Kör smoke/acceptanstester för de fem runtimepaketen där hostkapacitet finns. Fysisk Sparx-import förblir separat kontroll.

## 5. Dokumentation och filhygien

- Uppdatera `README.md`, `PROJECT.md`, `STATUS.md`, `project-status.yaml`, utvecklingsplanen och runtime-parity-rapporten efter verifierade ändringar.
- Märk tidigare Custom GPT-material som historiskt och ta bort inaktiva buildtargets först när de inte längre refereras.
- Granska överlapp mellan projektets lokala distributionsskript och officiell motor; ta inte bort scripts utan belagd ersättning och tester.
- Behåll historiska 19 steg för spårbarhet; lägg migreringen som separat maintenance-aktivitet.
- Säkra GitHub Actions versionspinning och undvik att `push` och `pull_request` dubblar samma arbete på samma branch.

## 6. Slutverifiering / merge-gate

Migrationen är klar först när alla fem distributionsarkiv faktiskt byggts och validerats, produktens deterministiska regressionstester passerat, dokumentationen är uppdaterad och alla kvarvarande externa begränsningar redovisats. En grön engine-selftest är **inte** tillräcklig.

## Nästa konkreta arbetssteg

Migrera `gpt-project.yaml` till fem peer-runtimes och modulariserad canonical instruktion med spårbarhet mot `assistant/instructions.md`. Implementera originalmotorns versionslåsta installerare, bygg och validatorer i CI. Generera artefakter och uppdatera status **först efter** verifierad build.
