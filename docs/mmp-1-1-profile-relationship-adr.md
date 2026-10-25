# ADR – MMP 1.1-spårets profilkontrakt och avancerad relationssemantik

- Status: **Accepted for implementation design** (inte release- eller konformitetsgodkännande)
- Datum: 2026-10-25
- Berör: CORE-013, CORE-015, CORE-016
- Föregångare: `docs/mmp-version-compatibility-decision.md`, `docs/mmp-1-1-archimate-gap-plan.md`

## Beslut 1: Paketformat och profiler

1. Behåll **MMP package_format_version 1.0.0** oförändrat för alla befintliga paket och konsumenter.
2. Utveckla ny semantik som versionssatta **opt-in-profiler**, och reservera `1.1.0` som framtida paketformat endast efter separat och verifierat kompatibilitetsbeslut. Kit-version `1.1.0` är en separat axel.
3. Nya regelpaket som *kräver* den avancerade semantiken får **inte** presenteras som fullständigt tolkningsbara av en 1.0-konsument. Innan produktion måste kritiska kapabilitetskrav vara kryptografiskt bundna till innehållet via befintligt checksummekontrakt eller motsvarande fail-closed mekanism.
4. En profil vars obligatoriska delar inte kan hanteras ger `not_supported`, inte `passed` eller tyst nedgradering. Förbehandlingskontroll måste ske före semantisk import/validering. En rent metadataorienterad `inspect` kan fortfarande vara möjlig.
5. **Release gate:** Inga nya MMP-profilpaket får marknadsföras som fullt verifierade förrän Python och TypeScript gör samma hela-paketstest mot giltiga, ogiltiga och okända obligatoriska profiler.

### Avgränsning

Detta ADR definierar målsemantik och gate, **inte** en fungerande syntax i dagens MMP 1.0-manifest. Den framtida profilmekanismens konkreta wireformat, signatur/integritetskoppling och versionsförhandling måste fastställas och implementeras före användning. Befintliga MMP 1.0-filer förblir giltiga enligt publicerat kontrakt.

## Beslut 2: CORE-015 – typberoende relationskombinationer

Definiera en generisk **pairwise relationship profile** med exakta tillåtna tripplar `(source_kind+type, relationship_type, target_kind+type)`:

- Använd en explicit tillåten mängd som enda auktoritativa källa inom profilen. Marginalprojektionerna `source.types` och `target.types` får **inte** generera kartesisk produkt när en pairwise-profil är aktiv.
- Utebliven trippel i en komplett deklarerad allow-set är förbjuden, men saknad profil i ett äldre paket betyder **inte** att gamla MMP-regler ändrar betydelse.
- Referenser kan avse konkreta och abstrakta typer. Definiera explicit transitiv subtypsmatchning; deduplicera normaliserade tripplar stabilt. Definiera konflikter med relationstypsarv och multipelt arv innan runtimeportning.
- Tillåt ett enkelt, läsbart canonical uttryck och en kompakt, **förlustfri** matrisprojektion. Båda måste ha samma normaliserade semantik och golden-resultat.
- Bevara källproveniens och status för direkta/härledda källregler; **härledning är inte del av CORE-015-exekvering**.
- Modellkompatibilitetsdiff som avlägsnar tillåtna tripplar ska klassas brytande eller `needs_review`, inte automatiskt kompatibel.

### Illustrativ syntax (inte implementerad)

```yaml
relationships:
  - id: assignment
    source: {types: [business_role, application_component]}
    target: {types: [business_process, application_function]}
    extensions:
      mmp_pairwise_candidate:
        allowed_type_pairs:
          - {source: business_role, target: business_process}
          - {source: application_component, target: application_function}
```

Syntax ovan **är en designskiss**. Ett nuvarande MMP 1.0-package kan bära `extensions`, men konsumenter som inte känner till skissen får inte påstå att de verkställt begränsningen.

## Beslut 3: CORE-016 – typade relationsändpunkter

En ändpunkt ska ha en explicit **category** och en **type-id**. Minsta målkontrakt omfattar:
- `element_type`: vanlig elementtyp.
- `relationship_type`: relation som ändpunkt.
- `junction_type`: särskild kopplingskonstruktion, separat från vanliga elementtyper.

Junctions är en **förstaklassig typkategori** i den föreslagna profilen; lösningen får inte tyst göra dem till element. Tillåtna kopplingar ska fortfarande prövas i CORE-015:s normaliserade relationstrippelmodell. Kategori och referensidentitet måste valideras, och `directed` och `navigable` behåller sina egna semantiska betydelser.

Vilka junction-operatörer, anslutningskardinaliteter och regler om relation-till-relation som blir normerande kräver separata testfall före implementation. Enbart stöd för kategorin är **inte** bevis för full instanskonformitet.

## Utanför MMP Core 1.1

- Traversal och härledning genom relationskedjor: separat framtida `mmp-relationship-derivation` profil.
- Full OCL-/naturligt-språksexekvering: separat rules-profil.
- Fullständig modellinstansvalidering inklusive antal relationer per instans: separat scope och CORE-007-beslut.

## Implementation och testgates i följande PR:ar

1. Fastställ maskinläsbar schema-/profilrepresentation för CORE-013 och wire-level krav som skyddar mot tyst nedgradering.
2. Utöka canonical schema och semantisk validator för CORE-015 med abstrakta typer, normalisering, felaktiga referenser och typkombinationer.
3. Utöka med CORE-016:s typade ändpunkter och negativa fall.
4. Koppla MMP export, import och referenskonsumenter till fullpaketkonformitet; Python/TypeScript ska producera samma normaliserade resultat.
5. Lägg till verkliga golden fixtures från versionslåst, licensmässigt användbart ArchiMate 3.2-underlag; källmatrisens siffror ska verifieras, inte antas som normativt facit.
6. Kör MMP 1.0-regression separat samt uppdatera readiness och releasegate. `PARTIAL/NO-GO` kvarstår tills körd testtäckning visar annat.

## Varför denna väg

Vi undviker parallella format och undviker att en konsument ignorerar affärskritiska relationsbegränsningar. MMP 1.0.0 hålls stabilt, medan komplicerade metamodeller kan kräva en uttrycklig, prövbar profilsupport.

## Konsekvenser

- Fler profiler och tydlig negotiation ökar implementationsarbete men ger interoperabilitet med explicit begränsning.
- Ett separat profilkontrakt kan senare kräva ett nytt minor-/major-formatbeslut; det är inte förhandsavgjort.
- CORE-015/016 är arkitekturbeslut, inte levererad runtimefunktion. Release status för MMP 1.1 är fortsatt **NO-GO**.
