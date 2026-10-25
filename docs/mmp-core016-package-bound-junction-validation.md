# CORE-016 – paketbunden junctionprofil som indata för instanskontroll

Den här etappen binder ihop MMP 1.1-kandidatens förhandlade `mmp-junction-structure@0.1.0`-dokument med den frivilliga strukturella junctionvalidatorn. Efter verifierad export/import läses operatörsmappningen från det checksummeskyddade paketet, inte från påhittade `operator`-fält i Core. `scripts/mmp_junction_profile_validation.py` projicerar operatörerna till en separat in-memory-modell; originalet ändras inte.

Paketeringstestet `scripts/test_mmp_junction_profile_graph_package.py` exporterar en kandidat, validerar MMP-manifest och import, hämtar dess faktiska YAML och JSON, och kontrollerar positiva och negativa instansgrafer. I TypeScript-workflow körs motsvarande bedömning i en separat TypeScript-evaluator med exakt samma data som extraherats från paketet. Saknad eller inkonsistent operatorprofil avvisas som `not_supported`, inte tyst som standardoperatör.

Detta verifierar **strukturell in-/utgrad**, inte AND/OR-aktivering, flödessemantik, ArchiMate-konformitet eller instansgrafens påstådda fullständighet. Den tidigare fristående strukturvalidatorn och Core-schemat är oförändrade. Ingen MMP 1.0-förändring eller äldre YAML-migrering. MMP 1.1 är fortsatt PARTIAL / NO-GO.
