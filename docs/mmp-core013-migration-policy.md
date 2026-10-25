# CORE-013 – kompatibilitetsgrind och migrering (implementationsetapp 1)

## Omfattning
Detta är **en konservativ säkerhetsgrind, inte färdig CORE-013-förhandling**. Paketen förblir MMP 1.0.0. Funktionen `scripts/mmp_capability_policy.py` inför ingen förändring av befintlig canonical YAML-struktur och ändrar inte definitionen av dagens YAML-fält.

- Tidigare modeller utan `metamodel.extensions.mmp_required_capabilities` behandlas precis som tidigare. Ingen automatisk omskrivning eller versionshöjning.
- Övriga existerande `extensions` bevaras oförändrade.
- Tom deklaration accepteras.
- Icke-tom kritisk deklaration avvisas av export och import med `not_supported`, även om kapabiliteten verkar bekant. Full 1.0-konsument får **inte** felaktigt godkänna funktioner den inte kan verkställa.
- Kontroll av import görs efter manifest- och SHA-kontroll, före ordinarie semantisk validering och innan något skrivs till arbetsytan.
- Exportens kontroll sker innan paket skrivs.
- `inspect` fortsätter att ge paketmetadata men garanterar inte semantisk profilkontroll; `validate` och `import` kontrollerar deklarationen.

## Viktigt säkerhetsförbehåll
Detta skyddar de två ändrade Metamodel Builder-skripten, **inte redan distribuerade eller oberoende MMP 1.0-konsumenter**. En gammal konsument kan fortfarande ignorera extensionfält. Därför måste profilkrävande paket blockeras från produktionsdistribution tills en verkligt paketbunden och fail-closed versionerad wire-kontraktmekanism är implementerad och verifierad i såväl Python som TypeScript. Detta steg löser inte CORE-013:s fulla acceptanskriterier.

## Framtida migrationsstrategi
1. Inventera gamla canonical YAML enligt schema_version=1 och MMP 1.0-paket. Låt dem vara giltiga utan omskrivning.
2. När nya fält/profiler införs: specificera exakt fältmappning samt dry-run-konvertering och explicit `--output` till ny arbetsyta. Skriv aldrig över originalet.
3. Kräv kontrollsummor före/efter migrering, diff av typer/relationer, och roundtrip genom båda konsumenterna.
4. Inga syntetiska `allowed_type_pairs` får skapas ur `source.types × target.types`; informationsbristen ska signaleras och kräva explicit val.
5. Lägg testfixtures för 1.0 canonical, 1.0 MMP, befintliga extensions, unsupported-profil, felaktig deklaration och misslyckad migrering.
6. Framför allt: ett paket som kräver utökad semantik måste uttryckligen signalera det i ett integritetsskyddat obligatoriskt kontrakt som en gammal konsument *inte* kan feltolka som fullständigt 1.0.

## Nästa etapp
Designa/implementera faktisk paketbunden profilförhandling i nytt versionskontrakt, med Python/TypeScript-paritet; behåll regression för alla 1.0-paket. CORE-013 är fortsatt **PARTIAL** och MMP 1.1 fortsatt **NO-GO**.
