# MMP Core – sammanhållen semantisk delkonformitetssvit

Detta är ett **körbart verifieringsunderlag**, inte ett anspråk på full MMP 1.1-konformitet. Befintlig MMP 1.0.0 och dess nio ZIP-paket i baslinjesviten påverkas inte.

## Underlag

- `conformance/core-semantic-suite-v1.json` har ett unikt testfalls-ID, länk till språkneutral vektor, kommando för respektive implementation samt en eller flera CORE-kravreferenser.
- `scripts/run_mmp_core_semantic_suite.py` kör samma hjälpfunktionstester i Python och (med `--typescript`) Node.js efter TypeScript-build.
- `--json-out reports/core-semantic.json` genererar PASS/FAIL per språk och fall, samt status per CORE-001–014. Fall utan vektortäckning får `not_tested`.
- Kravens statiska readiness-status från `conformance/mmp-1-1-readiness.json` ändras inte automatiskt av testresultat. Därför betyder PASS endast att en begränsad kandidatsemantik fungerar.

## Köra

```shell
python scripts/run_mmp_core_semantic_suite.py --json-out /tmp/mmp-core-python.json
cd interop/typescript && npm install && npm run build && cd ../..
python scripts/run_mmp_core_semantic_suite.py --typescript --json-out /tmp/mmp-core-both.json
```

**Avgränsning:** Dessa 9 semantiska testgrupper testar hjälpfunktioner, inte fullständiga importerade ZIP-paket mot strikt Core. Det automatiska testet verifierar resultat mot gemensamma golden-vektorer i båda språken; kompletta ZIP-negativfall och instansdata saknas fortfarande. CORE-001/002/005 har separata 1.0.0-tester, men markeras här som `not_tested` för just denna semantiska delsvit. CORE-012 saknar exekverbar normativ regelprofil.

## Frisläppningsgrind

Rapporten anger alltid `full_core_conformance: not_verified` och `release_decision: NO-GO` tills en ny normativt komplett svit, profilavgränsning och separat releasegranskning finns. CI-grönt test får inte likställas med formatkonformitet.
