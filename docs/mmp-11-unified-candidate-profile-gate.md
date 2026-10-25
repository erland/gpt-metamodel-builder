# Gemensam releasegrind för deklarerade MMP 1.1-kandidatprofiler

**Status: kandidattest, inte full MMP 1.1 Core-konformitet eller release-GO.**

Den här grinden kör verkliga ZIP-paketbaserade acceptanstester för följande redan implementerade delmängder: exakta relationspar, typade ändpunkter, typade par och deras arv, junction-profil och dess grafkoppling samt required/default-närvaroprofil. Varje underliggande test ansvarar för sina egna positiva och negativa paketfall. Saknade eller felaktiga obligatoriska profiler får inte ignoreras.

Kör `python scripts/test_mmp_11_candidate_release_gate.py --report /tmp/profile-gate.json`. Med `--typescript` körs även de underliggande TypeScript-kontrollerna, efter att TypeScript-projektet byggts. Skriptet fortsätter efter fel och skriver en maskinläsbar sammanställning där varje underkontroll får en separat PASS/FAIL-status.

## Förutsättningar och gränser

- Paketformat 1.0.0 verifieras av den **separata befintliga regressionssviten**; den här grinden får inte ensam användas som kompatibilitetsbevis.
- Den testar deklarerad paket- och profiltransport samt avgränsade semantiska instansfall, inte komplett generell instansgrafsvalidering.
- För en stabil release behövs fortfarande ett normativt scopebeslut, versionsfrysning och en sammanhållen slutlig GO/NO-GO-bedömning.
- Varken detta test eller ett grönt CI-resultat innebär oberoende extern certifiering.

**Releasebeslut: fortsatt PARTIAL / NO-GO.** Alla nya filnamn och testbeskrivningar är generiska.
