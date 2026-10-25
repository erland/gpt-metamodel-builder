# CORE-007/016 – gemensam konformitetssvit för typade instansgrafer

Den gemensamma testfilen `interop/core007-typed-graph-v1.json` använder en komplett, syntetisk instansgraf där element, relationsinstanser och junctions förekommer samtidigt. Python-testet kör befintliga `validate_typed_graph`; TypeScript-testet är en oberoende evaluator av samma **avgränsade kandidatkontrakt**. Båda konsumerar samma språkneutrala fall och måste få samma `accept`, `reject`, `error` eller `not_supported`.

Testfallen täcker tillåtna kopplingar, minimumkardinalitet inklusive nollincidens, saknad fullständighetsförklaring, ogiltig junction-typ, dinglande relationsreferens, felaktig endpointdomän, dubblerade relationsinstans-ID och otillåten typkombination.

**Begränsningar:** Denna testsvit bevisar varken full ArchiMate-junctionsemantik (AND/OR), topologiska cykler, relationstypsarv i instansgrafen eller att en extern källa verkligen är komplett när `complete: true` anges. MMP 1.1 förblir **PARTIAL / NO-GO**. Inga MMP-scheman eller äldre canonical YAML ändras; ingen migrering behövs.
