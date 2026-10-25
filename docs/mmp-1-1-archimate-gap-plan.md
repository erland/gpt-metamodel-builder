# MMP 1.1 – konsoliderade krav och ArchiMate 3.2 som acceptansfall

Status: **planeringsunderlag / NO-GO för full 1.1-konformitet**. Inga schema- eller runtimeförändringar i denna PR.

## Utgångsläge (main)
- MMP-paketformat är **1.0.0**; Specification Kit **1.1.0** är en separat versionsaxel.
- Testade delmängder: identitet, effektivt arv och properties, kardinaliteter, defaultvärden, relationsroller och navigerbarhet, extensionförhandling samt interoperabilitet i Python/TypeScript.
- `docs/mmp-strict-core-coverage.md` redovisar **PARTIAL/NO-GO**. Fristående semantiktestvektorer är inte bevis för att en hel paketkonsument upprätthåller regeln.
- Äldre projekts 19 utvecklingssteg är avslutade; MMP 1.1 är ett **separat aktivt arbetsområde**.

## Mål och avgränsning
MMP ska kunna (1) bevara en fullständig metamodell utan förlust, (2) strukturellt/semantiskt kontrollera dess definitioner och (3) erbjuda uttryckliga, profilerade förutsättningar för instansvalidering. Full modellinstansvalidator och full härledningsmotor behöver inte ingå i Core.

**Beslut att bereda:** om 1.1 är opt-in semantikprofil ovanpå 1.0.0 eller ny formatminor. Ändra inte giltigheten hos redan publicerade 1.0.0-paket i tysthet. För krav som påverkar en 1.0.0-konsuments möjlighet att tolka paketet korrekt krävs förhandlad, paketbunden kritisk profil.

## Kravregister (översikt)
| ID | Status från existerande underlag | Måste lösas för full 1.1? |
|---|---|---|
| CORE-001–006 | Blandad testad delmängd; full paketkonformitet ej styrkt | Ja |
| CORE-007 | Öppen: rollbaserad instanskardinalitet och relationsarv | Ja |
| CORE-008 | Testad delmängd av kardinalitetsparser | Ja |
| CORE-009 | Beslut krävs: required/default/kardinalitet | Ja |
| CORE-010–011 | Delmängd av default-/värdetester; canonicalisering ej klar | Ja om ingår i deklarerad Core |
| CORE-012 | Öppen: regelmotor kontra explicit not_supported | Besluta scope |
| CORE-013 | Beslut krävs: kritiska extensionkrav knutna till paket | Ja |
| CORE-014 | Delmängd: diff/kompatibilitetsanalys | Ja för deklarerade guarantees |
| **CORE-015** | **Nytt krav: pairwise relationship constraints** | **Ja för ArchiMate** |
| **CORE-016** | **Nytt krav: typed relationship endpoints** | **Ja för ArchiMate** |

### CORE-015 – exakta relationskombinationer
Ett deklarativt, generellt, språkneutralt kontrakt ska beskriva vilka trippelkombinationer `(source_type, relationship_type, target_type)` som är tillåtna. Två fristående endpoint-typmängder är inte likvärdigt. Specificera:
- explicit allow-set (och eventuell abstrakt typ med ärvda subtyper), samt default vid frånvaro; inga dolda korsprodukter får hävdas som exakt regel.
- relationstypsarv, multipelt arv, konfliktpolicy, reglernas komposition/försnävning och effektiv typupplösning.
- deterministisk kontroll av okända/abstrakta referenser, dubbletter, cykler samt positivt/negativt semantiskt resultat.
- stabil, maskinläsbar representation som fungerar med stora matriser och stödjer oförlustfri export/import/roundtrip.
- förändrade tillåtna kombinationer i modelldiff ska ge breaking/needs_review enligt effekt på befintliga modeller.

**Acceptans:** samma tillåt/avvisa och normaliserade tillåtna mängd i Python/TypeScript för gemensamma golden fixtures; gammalt MMP 1.0-testmaterial oförändrat.

### CORE-016 – typade relationsändpunkter
Modellen ska kunna skilja elementändpunkter, relationsändpunkter och särskilda kopplingskonstruktioner (t.ex. junctions) utan att använda artificiella elementtyper. Specificera:
- explicit endpoint-kategori + referensidentifierare samt validering av typ och identitet;
- riktning och navigerbarhet oberoende av kategorin;
- regler för relation-till-relation och junctions i generiska termer;
- hur en konsument utan denna semantik måste rapportera `not_supported` och inte hävda full import.

**Acceptans:** representera och roundtrippa testfall med relation som ändpunkt och en junction, inklusive negativa referens- och typfall i både Python/TypeScript.

## ArchiMate 3.2 som acceptansfixture
ArchiMates öppna implementation `relationships.xml` används **enbart som separat, spårbar tredjepartsfixture**, inte som normativ The Open Group-verifiering. Inventera exakt konceptmängd, typmappning och relationstrippel; dokumentera skillnader och proveniens. Den tidigare arbetsmatrisen omfattade 62 koncept, där `Relationship` och `Junction` inte var vanliga element, samt 3 841 icke-tomma source/target-par. Kontrollera om dessa siffror håller mot versionslåst källa innan de används som releasegate.

Acceptanskedja: importerad deklarativ representation → schema/semantik → MMP-export → säker MMP-import → Python/TypeScript fullpaket-konformitet → bytejämförelse/normaliserad paritetskontroll. Ingen `PASS` för ej körd instansvalidering eller härledning.

## Föreslagen arbetsordning
1. **Nästa PR:** fastställ 1.1 versions-/profilbeslut (inklusive kritiska profilkrav, CORE-013), samt schemaförslag för CORE-015/016; inga dolda major-brytningar.
2. Implementera pairwise schema och validator och gemensamma golden-testvektorer (CORE-015).
3. Implementera typade endpoints och junction/relationship-referenser (CORE-016).
4. Slutför gamla CORE-007/009/010/011 och utvärdera CORE-012 som separat derivation-profil.
5. Koppla krav till säkert MMP-manifest, import/export, två kompletta konsumenter, diff och negativa paketfall.
6. Uppdatera readiness-matris, regressionstesta MMP 1.0 och kör en fullständig releasegate. Ingen 1.1 full Core-claim innan återstående krav faktiskt verifierats.

## Spårbarhet
- `docs/mmp-core-1-1-readiness.md`
- `docs/mmp-1-1-readiness-review.md`
- `docs/mmp-strict-core-coverage.md`
- `conformance/mmp-1-1-readiness.json`
- `docs/mmp-relation-inheritance-policy.md`
- `docs/mmp-relationship-semantics.md`
- `docs/mmp-extension-negotiation.md`
- `schemas/metamodel.schema.json`

Inga av kraven ovan får märkas implementerade eller verifierade bara för att de dokumenteras i denna PR.
