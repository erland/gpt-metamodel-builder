# CORE-007/016 – cykelpolicy för relationsinstanser

Den frivilliga typade instansgrafsadaptern kan representera att en relationsinstans refererar till en annan relationsinstans. Men en cykel i dessa beroendereferenser har ännu ingen normativt fastställd semantik. Därför avvisar Python och TypeScript sådana cykler som `not_supported`, inklusive självreferenser. Andra ogiltiga referenser fortsätter att ge `error`.

En riktad beroendekant `A → B` finns när relationsinstansen A har source eller target med `{kind: relationship, id: B}`. En acyklisk kedja är fortsatt tillåten. Testfallen är gemensamma i `interop/core007-typed-graph-v1.json`.

**Avgränsning:** Det här är inte ett generellt förbud mot cykler mellan element i en arkitekturmodell. Det gäller endast rekursiva **relationsinstansreferenser** i den frivilliga instansgrafskandidaten. Junctions kan fortfarande förekomma på båda sidor av kopplingar; AND/OR-operationer, flödessemantik och junction-cykelpolicy är ännu inte specificerade.

Canonical YAML, MMP 1.0 och befintliga metamodeller påverkas inte; ingen migrering görs. Status för MMP 1.1 förblir **PARTIAL / NO-GO**.
