# CORE-016 – Förhandlingsbart kontrakt för exakta typade par

MMP 1.1-kandidaten kan nu transportera `allowed_typed_pairs` när modellen uttryckligen deklarerar båda kapabiliteterna `mmp-typed-endpoints@1.0.0` och `mmp-typed-pairs@1.0.0`. Kapabiliteterna ingår i canonical YAML och matchas mot manifestet. Export till MMP 1.0 avvisas.

Python- och TypeScript-konsumenterna kontrollerar att varje typat par ligger inom `typed_refs` för sin ändpunkt, avvisar dubbletter, förbjuder blandning med `allowed_type_pairs` och avvisar okända obligatoriska kapabiliteter. Pakettestet verifierar opt-in-export, import, båda konsumenterna och bytebevarande canonical YAML. Äldre modeller migreras inte automatiskt.

**Begränsning:** Semantiken är i detta steg exakta deklarerade par – inte transitive expansion av relation/junction-typer eller instansvalidering. MMP 1.1 är fortsatt PARTIAL/NO-GO tills detta och bredare negativa kompatibilitetsfall verifierats.
