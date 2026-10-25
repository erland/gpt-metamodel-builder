# CORE-013 – versionsmärkt MMP 1.1-kandidat (implementation, ej release)

## Syfte
Inför ett **opt-in kandidatpaket** med `package_format_version: 1.1.0` och en manifestbunden lista `required_capabilities`. Grundformatet MMP 1.0.0, befintliga canonical YAML-filer och äldre import/export-flöden lämnas oförändrade.

## Kontrakt
- `schemas/mmp-manifest-v1.schema.json` gäller fortsatt MMP 1.0.0 oförändrat.
- `schemas/mmp-manifest-1-1-candidate.schema.json` definierar kandidatmanifestet med obligatorisk lista av `{id,version}`.
- `export_mmp.py --candidate-1-1` skriver experimentellt manifest; utan flaggan skrivs exakt den tidigare MMP 1.0.0-strukturen.
- MMP 1.1-kandidatens `required_capabilities` måste vara lika med `metamodel.extensions.mmp_required_capabilities` (eller [] när fältet saknas). Därigenom ingår deklarationens kanoniska motsvarighet i kontrollerat SHA-256-filunderlag. Detta är **integritetskoppling, inte signatur/autentisering**.
- Paketens gamla `manifest.yaml` och hashes verifieras innan konsumtion. Saknad/missmatchad deklaration eller icke-tom obligatorisk profil ger `not_supported`; vi låtsas inte att avancerade regler har implementerats.
- `inspect` får visa metadata utan att exekvera semantiken. `validate` och `import` kontrollerar kandidatprofilen före skrivning.

## Äldre canonical YAML och MMP 1.0
- Ingen schema_version-höjning eller automatisk omskrivning.
- Inga gamla modeller får nya fält vid vanlig export/import.
- Canonical `extensions` som inte är kritiska ska bevaras; det nya kravet är endast opt-in.
- Ingen generering av `allowed_type_pairs` från gamla ändpunktsmängder; informationen finns inte i 1.0.
- Gammalt 1.0-paket behöver inte migreras till 1.1. Om framtida konvertering begärs ska den skriva en **ny** arbetsyta och redovisa semantiska luckor.

## Verifiering i PR
`scripts/test_mmp_core013_candidate.py` kontrollerar gammalt 1.0-paket, kandidatpaket, roundtrip, oförändrad YAML, stopp för överskrivning, manifest/canonical-mismatch, unsupported kritisk profil och fristående Python-konsument. TypeScript-konsumenten har motsvarande fail-closed-kod men fullständiga gemensamma 1.1-acceptansfixtures återstår.

## Begränsning
Detta är INTE produktionsklar MMP 1.1 eller full CORE-013. Ingen obligatorisk avancerad profil går än att importera som `supported`. Nästa steg behöver implementera semantikprofiler (CORE-015/016), förhandling med faktisk `supported`-mängd, fullpaketfixtures för både Python och TypeScript samt regressionsprövning för distributionerna.

**Releasegate kvarstår: PARTIAL / NO-GO.**
