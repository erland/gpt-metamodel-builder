# MMP Core – kanonisk värdesemantik (profilerat förslag)

Status: **frivillig kandidatprofil**, inte publicerad MMP 1.1.0 och inte en förändring av MMP 1.0.0-inläsning. Den här avgränsade profilen behandlar *textrepresentationer* av värden och bygger inte om JSON-/YAML-serialisering.

- **Integer:** strikt decimal heltalsnotation utan ledande nollor eller `-0`. Som portabel miniminivå använder vi intervallet ±9 007 199 254 740 991 eftersom TypeScript Number inte kan representera större heltal exakt. Det är ett **föreslaget profilval**, inte en begränsning som fanns i MMP 1.0.0.
- **Decimal:** enbart vanlig decimalnotation utan exponent. Avslutande nollor tas bort och negativ noll normaliseras till `0`. Beräkningen sker textbaserat utan floating-point, så precision går inte förlorad vid själva normaliseringen. Numeriska beräkningar eller maxprecision är inte definierade.
- **Date:** ISO-liknande `YYYY-MM-DD`, kontroll av faktisk kalenderdag; ingen lokal tidszon.
- **Datetime:** `YYYY-MM-DDTHH:mm:ssZ` eller numerisk offset; normaliseras till UTC i hela sekunder. Fraktioner och leap seconds är inte specificerade i denna kandidatprofil.
- **URI:** begränsad till HTTP(S), normaliserar schema och värdnamn till gemener. Övriga URI-scheman, internationella domäner, IPv6, escape-kodning och full RFC-jämförelse kräver senare normativa beslut. Detta är **inte** en generell URI-kanonisering.

Gemensamma testvektorer finns i `interop/canonical-values-v1.json` och körs av oberoende Python- och TypeScript-implementationer i CI. Passerade vektorer styrker endast denna begränsade delmängd; MMP Core 1.1 förblir **inte färdig**.
