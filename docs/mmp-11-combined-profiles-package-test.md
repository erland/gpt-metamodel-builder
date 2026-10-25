# Kombinerat MMP 1.1-kandidatpaket med obligatoriska profiler

Det interna acceptanstestet `scripts/test_mmp_11_combined_profiles_package.py` bygger ett **enda verkligt kandidatpaket** som samtidigt kräver:

- `mmp-typed-endpoints@1.0.0`
- `mmp-typed-pairs@1.0.0`
- `mmp-junction-structure@0.1.0`
- `mmp-required-default-presence@0.1.0`

Testet kontrollerar export, manifestets deklarationer, profiler i paketet, Python-importvalidering, Python-konsument, canonical byteidentisk import och (med `--typescript`) TypeScript-konsument. Det kontrollerar också att manipulation av ett profilschema eller kritisk deklaration inte accepteras med oförändrade checksummor, att en okänd deklarerad profilversion inte får exporteras och att detta innehåll inte kan nedgraderas till MMP 1.0.

**Avgränsning:** Detta är ett strukturellt och paketbundet samverkansprov. Det bevisar inte generell instanssemantik, junctionoperatorernas beteende eller fullständig MMP Core-konformitet. Den befintliga releasebedömningen förblir villkorat NO-GO tills versionsfrysning, slutar­tefakt och dokumentation är klara. Alla testtyper och namn är syntetiska och generiska.
