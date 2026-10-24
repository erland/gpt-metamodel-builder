# MMP Core – datatyper och standardvärden (utkast)

Status: **frivillig semantisk profil för interoperabilitet**, inte en retroaktiv ändring av MMP 1.0.0. Den befintliga 1.0.0-definitionen `default: {}` tillåter alla JSON-värden. Validerarna för paketimport ändras inte av denna PR.

## Kandidatregler

- `string`: text; `identifier`: icke-tom text. Ytterligare URI-/ID-normalisering återstår att definiera.
- `integer`: heltal, med booleska värden uteslutna. TypeScript accepterar bara säkert representerbara heltal; för full interoperabilitet behöver vi specificera ett gemensamt numeriskt intervall.
- `decimal`: ändliga numeriska värden, inte text och inte bool. Precision och kanonisering är ännu inte beslutad.
- `boolean`: endast `true` eller `false`.
- `date`: `YYYY-MM-DD` med verkligt kalenderdatum.
- `datetime`: `YYYY-MM-DDTHH:mm:ssZ` eller explicit numerisk UTC-offset. Fullständig datumtidssemantik inklusive leap seconds är inte slutligt definierad.
- `uri`: text med schemaprefix och utan blanktecken. Detta är en grundkontroll, inte en komplett RFC 3986-validator.
- `enumeration`: värdet måste vara ett deklarerat enum-ID, inte ett visningsnamn.

Med `cardinality` får en lista tolkas som flera värden och varje post kontrolleras mot sin datatyp. Ett skalärvärde motsvarar ett värde. Utan explicit kardinalitet accepterar denna begränsade profil endast ett skalärvärde. Värden av typen `null` och tomma listor kräver tydligare instans-/default-policy innan profilen blir normativ.

## Täckning

Golden-vektorerna i `interop/default-values-v1.json` körs mot två oberoende implementationer och ingår i specifikationspaketet. De omfattar positiva och negativa värden för alla basdatatyper, uppräkningar och kardinalitetsbegränsade listor.

**Ej löst:** värdeintervall för stora heltal, decimaltalsprecision, normalisering av identifierare/URI, generella mönster och gränsvärden i `data_types`, samt samspelet med `required`. Testerna utgör därför inte full MMP Core 1.1-konformitet.
