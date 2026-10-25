# CORE-015/016 – ärvda typade par tillämpas på instanskanter

Den frivilliga `validate_typed_graph` kontrollerar nu också effektiva typade par för relationsinstanser vars relationstyp har `extends`, även när barnet inte deklarerar egna `allowed_typed_pairs`. Effektiva par härleds via `mmp_effective_typed_pairs.effective_typed_pairs`: snitt av föräldrars deklarerade par samt eventuella barnbegränsningar, därefter filtrering på barnets typade ändpunktsdomäner.

För varje faktiskt relationsinstanspar sker exakt jämförelse av `{kind,id}`-typnycklar. Ingen tyst kartesisk produkt eller implicit subtypsutvidgning görs. Om en förälder saknar explicit eller ärvt par-kontrakt avvisas det som `not_supported`. Relationen utan `extends` och utan `allowed_typed_pairs` behandlas som tidigare: ingen typad parprofil antas.

Regressionstestet `scripts/test_mmp_inherited_pairs_instance_gate.py` provar accepterad kant, två förbjudna instanspar samt ett ofullständigt föräldrakontrakt. Här ändras bara Python-instansgrafsvalideringen: paketimportörer och TypeScript-instansgrafevaluator behöver motsvarande explicit integrering och fullpakettester innan konformitet kan styrkas.

Canonical YAML, MMP 1.0 och den separata junction-profilen ändras inte. MMP 1.1 är fortsatt **PARTIAL / NO-GO**.
