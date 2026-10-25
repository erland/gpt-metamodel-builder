# CORE-007 – typade relationsinstanser som ändpunkter (kandidatetapp)

Den frivilliga funktionen `scripts/mmp_typed_instance_graph.py:validate_typed_graph` använder en explicit komplett instansgraf där element finns i `instances` och **relationsinstanserna** är de identifierade posterna i `edges`. Typade ändpunkter anges med `{kind: element|relationship, id: instans-id}`; instans-ID måste referera till existerande element- respektive relationsinstans. Många relationer får referera till samma relationsinstans.

Validatorn kontrollerar referensintegritet, unika ID:n, deklarerat `typed_refs`-domänmedlemskap och exakta `allowed_typed_pairs` när sådana finns. Den räknar ändpunktsförekomster inklusive nolltal över explicit deklarerad population och återanvänder CORE-007:s intervallvalidator. `complete: true` är fortfarande ett påstående från datakällan, inte ett oberoende fullständighetsbevis.

**Viktig avgränsning:** Junction-topologi avvisas `not_supported`. Element-/relationstypsarv, semantiskt rekursiva relation-till-relation-cykler, regler för räknande av relationstypsspecialiseringar och full instansvalidering av äldre `allowed_type_pairs` omfattas inte. Den nya adaptern är separat från den tidigare elementbaserade instansgrafsadaptern och används bara explicit. MMP-paketformaten och canonical YAML ändras inte; äldre modeller behöver inte migreras.

**Nästa steg:** Normera junction-instanser och topologi, policy för relation-instanscykler samt effektiva typer/ärvda par med delade Python/TypeScript-fixtures. CORE-007 är fortsatt **PARTIAL**, MMP 1.1 **NO-GO**.
