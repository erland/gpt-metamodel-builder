# Paketbunden närvaroprofil för required/default

**Status:** experimentell MMP 1.1-kandidat, inte generell Core-konformitet.

Den frivilliga, obligatoriskt förhandlade kapabiliteten `mmp-required-default-presence@0.1.0` kräver en separat dokumentfil `documentation/required-default-presence.json` med låsta värden `default_satisfies_required:false` och `null_counts_as_present:false`. Dessa metadata ingår i paketets befintliga checksummekontrakt.

Export avvisar frånvarande, odeklarerad eller ogiltig profildokumentation. Pythonimport och oberoende Python-/TypeScript-konsumenter avvisar saknad eller avvikande dokumentation samt okända obligatoriska profiler. Denna pakettolkning är en **kapabilitetskontroll**, inte automatisk generell instansvärdesvalidering. Den tidigare språkneutrala instanspolicyn körs separat som testvektorer.

Äldre MMP 1.0-paket förblir oförändrade; den nya profilen får inte exporteras i 1.0-format. Release av full MMP 1.1 Core är fortsatt NO-GO.
