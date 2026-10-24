# MMP Core – kompatibilitetsbeslut inför 1.1

Status: **beslutsunderlag / preliminär policy**. Publicerad `package_format_version: 1.0.0` ändras inte. Detta dokument skiljer strukturell giltighet enligt 1.0.0 JSON Schemas från semantiska krav i en framtida strikt Core-profil.

## Tre kompatibilitetsnivåer

- **Clarification:** oförändrade tillåtna paket och oförändrad tolkning; får införas i dokumentationen för 1.0.x.
- **Opt-in strict:** lägger till regler som kan avvisa schema-giltiga 1.0.0-paket. Används endast när användaren/konsumenten uttryckligen begär den profilen; ett sådant utfall får inte felaktigt beskrivas som `invalid MMP 1.0.0`.
- **Major candidate:** förändrar innebörden av ett befintligt fält eller inför nya obligatoriska krav för generella konsumenter. Kräver separat kompatibilitetsbeslut och normalt nästa major-version.

## Beslutsregister

| ID | Område | Klass | Kontrakt för nästa profil | Risk/öppen fråga |
| --- | --- | --- | --- | --- |
| CORE-001 | Identitet | Clarification | Typens globala identitet härleds ur namespace och lokalt ID; `name` är etikett | Ändrad namespace är identitetsbyte |
| CORE-002 | Arvsgraf | Opt-in strict | Okända `extends`-referenser och cykliskt arv avvisas | Schema 1.0.0 kan acceptera sådana dokument |
| CORE-003 | Multipelt arv | Clarification | Effektiv supertypmängd är transitiv, deduplicerad mängd efter ID | Ordning i YAML ger ingen konfliktprioritet |
| CORE-004 | Property sets | Clarification | Samma property-definition-ID som ärvs flera gånger förekommer en gång; olika ID sammanförs aldrig med hjälp av `name` | Kräver separat test med diamantarv och likadana etiketter |
| CORE-005 | Konflikter | Opt-in strict | Dubbla definitions-ID och brutna referenser avvisas | Finns i Python/TS delvis, full profil ej styrkt |
| CORE-006 | Relationsroller | Clarification | `source` och `target` är skilda typbegränsade roller även när `directed=false` | Navigerbarhet måste hållas åtskild från riktning |
| CORE-007 | Endpoint-kardinalitet | Opt-in strict | Gränser kontrolleras semantiskt och rollbaserat; `n..m` måste ha `n<=m` | Tolkningen på instansnivå behöver exemplariseras |
| CORE-008 | Property-kardinalitet | Opt-in strict | `*` betyder `0..*`, `n` exakt n; om båda gränser anges måste min<=max | Schema 1.0.0 tillåter exempelvis `3..1` |
| CORE-009 | Required | Major candidate | `required:true` kontra `cardinality:0..*` måste få en beslutad prioritet; avvisa inte tidigare giltiga paket förrän beslutat | Nuvarande förslag att avvisa konflikter kan vara brytande |
| CORE-010 | Default | Opt-in strict | Kontrollera default mot egenskapens datatyp, enumeration och multiplicitet | 1.0.0-schema har obegränsat `default: {}` |
| CORE-011 | Datavärden | Major candidate | Datum/tid, numerisk precision och URI-normalisering behöver profilerade regler | Ingen interoperabel värdesemantik definierad |
| CORE-012 | Rules | Clarification | Oimplementerade uttryck får status `not_supported`; de får inte rapporteras som `passed` | Regelspråk behöver egen normativ profil |
| CORE-013 | Extensions | Major candidate | Namnrymder och kritiska tillägg behöver separat förhandlingsmekanism | `additionalProperties:true` tillåter idag godtycklig extension |
| CORE-014 | Ändringar mellan modellversioner | Clarification | Typer, ID, datatyper, obligatoriska egenskaper, kardinaliteter och endpoints jämförs semantiskt; osäkra fall `needs_review` | Fullautomatisk bakåtkompatibilitet är inte styrkt |

## Konkreta exempel på skillnaden

| Paketets innehåll | Schema 1.0.0 | Föreslagen strict Core | Kommentar |
| --- | --- | --- | --- |
| `cardinality: "3..1"` | Kan godtas | Avvisa | Strukturellt strängmönster ≠ numeriskt intervall |
| `required: true` och `cardinality: "0..*"` | Kan godtas | Ej beslutat | Måste få explicit prioritet före strikt gate |
| `default: "abc"` på ett heltalsattribut | Kan godtas | Avvisa | Exempel på typkontroll som inte finns i schemat |
| `extends` innehåller ett okänt ID | Kan godtas av schema | Avvisa | Semantisk referensintegritet |
| Diamantarv som ger samma property-ID via två vägar | Kan godtas | Godta, deduplicera | Deterministisk ID-baserad union |

`Kan godtas` betyder endast att det specifika JSON Schema-villkoret inte förbjuder konstruktionen. Andra filer, importer eller befintliga semantiska kontroller kan fortfarande avvisa ett helt paket.

## Go/no-go inför MMP 1.1.0

1. Fastställ återstående semantiska val för CORE-007, CORE-009, CORE-010 och CORE-011 innan anspråk på full Core-konformitet.
2. Utöka den gemensamma Python/TypeScript-sviten med accept-/reject-fall **per profilerad regel**, med explicit profil i manifestet. Blanda inte strikta tester med den befintliga niofallsbaslinjen för MMP 1.0.0.
3. Dokumentera mappning mellan konsumentens `supported/partial/unsupported` och faktiskt körda tester. `supported` kräver full täckning av profilens normerade kriterier.
4. Publicera inga ändrade scheman, `package_format_version` eller exporter-/importerpolicy som en tyst 1.0.0-ändring.
5. Kör samma testpaket på båda konsumenterna och jämför inte bara accept/reject utan även normaliserad semantisk tolkning av arv och egenskaper.

**Rekommendation:** Fortsätt först med fler positiva/negativa semantikfall och ett deterministiskt beräknat `effective properties`-resultat i båda konsumenterna. MMP 1.1 är inte releaseklar på basis av nuvarande nio testfall.
