# CORE-016 – Python/TypeScript-paritet för ärvda instanspar

Den befintliga TypeScript-instansgrafskonsumenten använder nu samma snäva beräkning av **exakta ärvda typade par** som infördes i Python i PR #79. Om relationstypen har `extends` eller `allowed_typed_pairs` beräknas snittet av samtliga explicita/ärvda parkontrakt och barnets typade ändpunktsdomäner. Saknat föräldrakontrakt avvisas `not_supported`, förbjudna verkliga relationer avvisas. Relationer utan typad parprofil får fortsatt sin äldre kontroll.

Gemensamma JSON-testvektorer i `interop/core016-inherited-instance-graph-v1.json` körs mot den faktiska Python-grafvalidatorn och TypeScript-grafevaluatorn. Tester omfattar accepterat par, förbjuden källa, förbjudet mål, ofullständig graf och saknat föräldrakontrakt.

**Begränsning:** Exakta `{kind,id}`-nycklar jämförs utan implicit subtypsutvidgning. Koppling till MMP 1.1:s fullständiga paketvalidering och externa konsumenter återstår. Ingen ändring av canonical YAML eller MMP 1.0; MMP 1.1 förblir **PARTIAL / NO-GO**.
