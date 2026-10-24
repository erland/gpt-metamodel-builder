# MMP Core – relationssemantik (förslag)

Det här är en frivillig semantisk testprofil, inte en ändring av publicerad MMP 1.0.0.

- `source` och `target` är distinkta typbegränsade roller, också för `directed:false`. Att relationen är oriktad innebär inte att endpoint-rollerna automatiskt kan bytas ut.
- En deklarerad tillåten elementtyp omfattar även alla dess transitiva subtyper; `abstract:true` hindrar direkt instansiering, men inte användning av den abstrakta typen som endpoint-typbegränsning.
- `directed` har standardvärdet `true` när fältet utelämnas.
- `navigable` och `directed` är separata begrepp. Saknad `navigable` redovisas som `null` (ospecificerat), inte `false`.
- Relationstypsarv måste fortsätta kontrolleras för okända supertype-referenser och cykler. **Ärvda endpoint-restriktioner, ändring av riktning och tillåten försnävning** är ännu inte slutligt normerade och tolkas därför inte implicit av testprofilen.

Den språkneutrala testvektorn `interop/relationship-semantics-v1.json` verifierar både effektiva endpoint-roller och tillåtna konkreta elementtyp-par i Python och TypeScript.

Full MMP Core-konformitet är inte styrkt av dessa deltester.
