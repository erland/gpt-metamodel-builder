# MMP Core – semantik och kompatibilitet (förslag till 1.1)

Status: **normativt förslag**, inte en retroaktiv ändring av publicerad MMP 1.0.0. Formatet är projektspecifikt. Denna text gäller definition av metamodeller, inte verifiering av en viss instansmodell.

## Tolkning och begrepp

- **Type ID:** `<namespace>#<RFC3986-escaped-local-id>`; visningsnamn får ändras utan identitetsbyte. Typ-ID för element och relationer får inte kollidera i samma modell.
- **abstract:** `true` betyder att typen inte får instansieras direkt i en konsument som hanterar instanser. Abstrakta typer är giltiga som supertype och i endpoint-typmängder; subtyper är tillåtna där supertypen tillåts.
- **extends:** riktad, acyklisk relation från undertyp till direkta supertyper i samma typkategori; okända referenser och arvscykler är semantiska fel. Flerarv är tillåtet när resultatet är entydigt.
- **effective type:** transitiv slutenhet av typens supertype-graf, inklusive typen själv. Beräkna med deduplicering av identiska typ-ID, oberoende av deklarationsordning.

## Egenskaper och egenskapsgrupper

- `property_definitions[].id` identifierar en global egenskapsdefinition i metamodellen. En `property_set` är en återanvändbar uppsättning referenser till sådana definitioner.
- En typs effektiva property sets är unionen av egna och samtliga ärvda property sets. Samma property-set-ID förekommer en gång i resultatet, även om det ärvs från flera håll.
- Effektiva egenskaper utgör unionen av egenskapsreferenserna i de effektiva grupperna. Två vägar till **samma property-definition-ID** ger en egenskap, inte två.
- En egenskap kan inte ändra datatyp, kardinalitet, required eller default enbart genom att refereras i en subtyp eller annan grupp. Ändring av global `property_definitions` ändrar alla användningar och måste versionsklassificeras.
- Om två globala egenskapsdefinitioner har olika ID men samma `name` är de **olika egenskaper**; konsumenten får inte slå ihop dem baserat på etikett. Det är ingen konflikt på ID-nivå.
- Dubblettdefinitioner av samma ID i samma samling är ogiltiga. Saknade referenser till property sets eller property definitions är ogiltiga.

## Relationer och ändpunkter

- `source` och `target` är skilda roller även om `directed: false`; ett odirektionellt relationsvärde innebär att instansrelationen saknar normativ traversalriktning. Det innebär **inte** att ändpunkternas typrestriktioner kan ignoreras.
- `endpoint.types` är en tillåten mängd deklarerade elementtyper. Subtyper omfattas transitivt. Tom typmängd är inte en wildcard och bör avvisas som semantisk ogiltighet.
- `navigable` anger navigationsstöd från en ändpunkt och är inte liktydigt med `directed`. Om `navigable` saknas är beteendet ospecificerat och får inte tolkas som `false`.
- För relationstyper som ärver från andra relationstyper är regler för eventuell **försnävning** av endpoint-mängder eller kardinaliteter ännu inte formellt specificerade. Det är inte legitimt att gissa sådant stöd och samtidigt hävda full MMP Core-konformitet.

## Kardinalitet och obligatoriska egenskaper

Gällande schemats textnotation för kardinalitet måste parsas som ett **antal värden/anslutningar**; `*` = `0..*`, `n` = exakt n, `n..m` = n till m inklusive, `n..*` = minst n. Alla gränser är icke-negativa heltal med `min <= max` när max är ändligt. Inga blanksteg eller alternativa intervallsyntaxer. En enskild värdeposition kan aldrig innehålla fler än en instans av ett enkelvärde.

- `property_definitions[].cardinality` reglerar antalet värden för varje instans av den typ som bär egenskapen, inte antalet property sets.
- `endpoint.cardinality` reglerar deltagande i relationer vid den rollen per relevant elementinstans, inte hur många olika elementtyper som får förekomma.
- `required: true` kräver minst ett explicit eller normativt defaultvärde vid instansvalidering; `required: false` uttrycker inte att högsta tillåtna antal är noll. Om cardinality har `min=0` och `required=true` uppstår en inkonsekvent deklaration och bör avvisas i en **framtida strikt profil**. Om cardinality saknas kan ingen högsta gräns härledas ur required.
- Ett `default` måste vid användning uppfylla datatypen och kardinalitetens högsta gräns; för `enumeration` måste värdet motsvara ett deklarerat enum-ID. Standardvärden är inte ett sätt att kringgå schema- eller referensvalidering.
- Precision för decimaler, datumtidszoner och normalisering av URI-värden är ännu **öppna preciseringar**. Ett verktyg får inte lova identisk roundtripsemantik på dessa utifrån 1.0.0 ensam.

## Constraints och osupporterade uttryck

Formatet deklarerar `rule.language` och `rule.expression`. I 1.0.0 finns ingen exekveringsstandard för `declarative`, `expression`, `ocl` eller `natural_language`. En konsument får alltid läsa och bevara regeltexten, men får bara rapportera `evaluated` när en publicerad och implementerad regelprofil finns och faktiskt har körts. I annat fall: `not_supported`; `not_applicable` används enbart när regeln verkligen inte är tillämplig på granskat objekt. Dessa statusvärden är rapporteringsvärden, inte schemafält som måste läggas till i varje constraint.

## Versions- och bakåtkompatibilitet

Två oberoende versionsaxlar: `package_format_version` (MMP-kontrakt) och `metamodel.version` (användarmodell).

- Kompatibla modelländringar kan vara ändrade etiketter och beskrivningar, tillägg av frivilliga egenskaper samt nya typer utan att befintliga typers tillåtna instanser begränsas.
- Potentiellt brytande modelländringar: byte av namespace eller lokalt ID, borttagna typer, ändrade egenskapsdatatyper, strängare minima/maxima, avlägsnade tillåtna relation-endpoints eller ändrat relationsriktning.
- En metamodelldiff som inte kan fastställa påverkan på konsumenters befintliga data måste klassas som `unknown/needs_review`, inte automatiskt `compatible`.
- Okända frivilliga extensions får bevaras eller ignoreras **endast** om producenten inte kräver deras semantik för korrekt tolkning. En sådan semantik kräver senare konformitetsprofil/förhandling.
- Förslag i detta dokument som gör tidigare giltiga 1.0.0-paket ogiltiga måste ligga i en **opt-in strikt profil** eller reserveras för ett nytt major-format. Ny MMP 1.1 ska inte ändra betydelsen av redan giltiga 1.0.0-fält.

## Utestående standardiseringsbeslut

1. Relationstypsarv och om endpoint-försnävning alls tillåts.
2. Explicit defaultvalidering, required/cardinality vid 1.0.0-konflikter och flerfaldiga defaultvärden.
3. Datum/tid, numerisk precision, gränsvärden och URI-jämförelse.
4. Extensions namnrymd, criticality och konsumentens hantering av okänd semantik.
5. Rule-profiler med exakta tolkningsregler.

Dessa frågor **får inte** tyst klassas som fullständigt specificerade MMP 1.0.0-regler.
