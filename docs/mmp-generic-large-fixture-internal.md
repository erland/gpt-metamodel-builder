# Stor intern strukturfixture – kandidatformat

Detta är ett **syntetiskt internt belastnings- och acceptanstest** för MMP:s generella metamodellegenskaper. Testdatan är inte en representation, distribution eller konformitetsgaranti för något externt modelleringsspråk.

## Omfattning och verifiering

En deterministisk generering skapar 49 nya elementtyper i sju grupper, två junctiontyper, sju nya relationstyper och 5 047 tillåtna typade relationspar. Existerande grundmodell behålls så dess viewpoints, constraints och andra referenser inte blir ogiltiga.

Testet kontrollerar att en komplett canonical modell kan:
- valideras och exporteras till ett MMP 1.1-kandidatpaket;
- valideras av importören och läsas av fristående Python-konsument och i separat CI av TypeScript-konsument;
- importeras igen utan att canonical YAML-bytes förändras;
- bevara antal definierade elementtyper och relationspar;
- avvisa en tyst nedgradering till MMP 1.0.

Fixturespecifikationen ligger under `tests/fixtures/`. Den är endast testdata och ingår inte som produktmodell, stöddeklaration eller exempelmetamodell för slutanvändare.

## Begränsningar

Detta provar volym, referenser, explicita typade par och paketbevarande. Det provar **inte** täckning av ett externt språks fullständiga typinventering, alla arvssituationer, verklig instansgrafsemantik, operatoraktivering eller oberoende extern konformitet.

Resultatet får inte användas som påstående om färdig MMP 1.1-konformitet. **Status: PARTIAL / NO-GO.**
