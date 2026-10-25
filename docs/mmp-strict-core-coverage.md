# PR #45 – Strict Core: slutlig täckningsinventering

**Bedömning: PARTIAL / NO-GO för MMP 1.1 full Core-konformitet.** Detta är avsiktligt en konsolidering snarare än ännu en semantisk utbyggnad. Publicerat MMP 1.0.0-kontrakt påverkas inte.

## Vad som faktiskt verifieras

Den strikta kandidatprofilen från PR #44 validerar först hela MMP-paket enligt den äldre konsumenten och utför sedan några uttryckligen striktare kontroller av intervall för property-/endpoint-kardinaliteter samt motsägelsen `required:true` vid max 0. Arvade property sets har separata paketbaserade acceptanstester. Underlagen körs i såväl Python som TypeScript.

Maskinläsbar källa: `conformance/strict-core-coverage-v1.json`; integritetskontroll: `scripts/test_mmp_strict_coverage.py`. Detta är inte ett automatiskt fullt kravbevis. Status `subset` innebär att enbart de uppräknade fallen täcks.

## Avgränsning inför release

| Krav | Fortfarande öppet |
| --- | --- |
| CORE-001 | Fullt identitetskontrakt på strikt paketnivå |
| CORE-006/007 | Relationers roller, arv och instansbaserad ändpunktskardinalitet |
| CORE-009/010 | Samspelet required/default och full värdevalidering vid paketimport |
| CORE-011 | Fullständig kanonisk värdehantering kopplad till paketdata |
| CORE-012 | Beslut om regelutvärdering är separat profil eller obligatorisk Core |
| CORE-013 | Pålitlig koppling mellan paket och kritiska extensionkrav |
| CORE-014 | Heltäckande kompatibilitetsklassificering mellan modellversioner |

### Rekommenderat releasebeslut

1. **Frys v1.0.0 som stabilt format.**
2. I PR #46: fastställ tydligt om v1.1 ska vara ett opt-in profilpaket ovanpå 1.0.0 eller en faktiskt ny paketformatversion. Undvik nya obligatoriska fält utan majorbeslut.
3. I PR #47: exportera komplett specifikationspaket, jämför Python/TypeScript-testresultat och dokumentera konformitetens exakt avgränsade status. Publicera inte v1.1 med full Core-konformitetsanspråk om ovanstående luckor kvarstår.

En grön CI-körning betyder här att dokumentation, verifieringskod och befintliga delsviter fungerar — **inte** att MMP 1.1.0 är redo.
