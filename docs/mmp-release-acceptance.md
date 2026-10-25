# MMP Specification Kit 1.0.0 – slutligt acceptansunderlag

Detta dokument beskriver **acceptansgrinden inför release**. Det är inte ett påstående att en GitHub-release redan har publicerats eller att det finns full MMP 1.1 Core-konformitet.

## Reproducerbart bygge och integritetskontroller

Kör `python scripts/test_mmp_release_kit.py` i källträdet med PyYAML och jsonschema installerade. Kontrollprogrammet bygger samma specifikationspaket **två gånger**, jämför ZIP-filerna byte för byte, kontrollerar den kompletta `SHA256SUMS.txt`-inventeringen och verifierar varje testpakets SHA-256 mot respektive testmanifest.

Kör sedan `python scripts/test_mmp_release_kit.py --kit /tmp/mmp-specification-1.0.0.zip` för att granska en redan byggd releaseartefakt. Båda lägena kan skriva JSON med `--json-out /tmp/mmp-release-acceptance.json`.

## Oberoende konsumenter

CI kör befintlig MMP 1.0.0-baslinje med nio positiva/negativa paket, ytterligare paketbaserade semantikfall och opt-in strikt kandidatprofil mot **både Python och TypeScript**. Den semantiska hjälpfunktionssviten testar vidare delmängder av CORE-001–014. PASS av dessa är inte ett heltäckande certifikat.

## Versionsbeslut

Paketformatet förblir **1.0.0**; framtida Strict Core-regler och övriga semantiska profiler är valfria och inte fullt normerade. Maskinläsbart versionsbeslut följer med specifikationspaketet. Publicering av MMP 1.1.0 eller `mmp-core: supported` med full konformitet är fortsatt **NO-GO**.

## Acceptansbeslut

En grön körning visar att specifikationspaketet är reproducerbart, integritetskontrollerat och fungerar med de två referenskonsumenternas testade delmängder. Den godkänner **releasekandidaten till MMP Specification Kit 1.0.0** med beskrivna begränsningar, inte en oberoende tredjepartscertifiering.

När PR är mergad kan en separat tagg/release publiceras med den byggda ZIP-filen och dess SHA-256. En release skapas inte automatiskt av denna PR.
