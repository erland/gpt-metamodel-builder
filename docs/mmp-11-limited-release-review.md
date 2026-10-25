# MMP 1.1 – slutlig avgränsad releasebedömning efter samlad kandidatgrind

**Beslut: villkorat NO-GO.** Bedömningen avser en stabil **avgränsad deklarativ paketversion 1.1.0**, inte fullständig MMP Core eller instansvalidering. Den är käll- och testbaserad och ingen extern certifiering.

## Verifierat inför bedömningen

PR #90 är mergad. Samma PR:s tre workflows (ordinarie CI, TypeScript-interoperabilitet och engine-preflight) slutfördes med PASS. Den gemensamma kandidaten `scripts/test_mmp_11_candidate_release_gate.py` sammanställer **sju paketbaserade testområden** för exakta par, typade ändpunkter och par, relationstypsarv, junctions och required/default-presence. Äldre MMP 1.0 testas separat. Grönt innebär att *de registrerade fallen* passerar, inte att alla hypotetiska modeller fungerar.

## Minsta återstående releasehinder

| ID | Releasekriterium | Varför det behövs |
| --- | --- | --- |
| RELEASE-01 | Frys versions- och scopekontraktet för **package format 1.1.0** respektive **Specification Kit** samt dess obligatoriska profilversioner | Hindrar tvetydiga kompatibilitetslöften |
| RELEASE-02 | Ett **kombinerat** kandidatpaket med flera samtidigt obligatoriska profiler, inklusive negativa fall, prövas i Python och TypeScript | Befintliga pakettester verifierar främst profiler var för sig |
| RELEASE-03 | Bygg slutlig avsedd 1.1-distribution från tagg och kör reproducerbarhets-/checksummegrind på samma artefakt | Kit 1.1.0 och format 1.1.0 är inte samma versionsaxel |
| RELEASE-04 | Städa status-/releasedokumentation och lista exakt vad som *inte* garanteras | Projektstatus innehåller fortfarande äldre utvecklingsprioriteringar |

## Vad kan skjutas upp?

Komplett instanspopulation/kardinalitet, utökad datatypexekvering, avancerad junction-aktivering, relationshärledning, generell regelmotor och oberoende extern certifiering. Det förutsätter att dessa funktioner uttryckligen **inte** ingår i den normativa 1.1-nivån och att senare stöd läggs till via versionssatta profiler utan retroaktiv omtolkning.

## Rekommenderad ordning

1. Definiera de sista releasegarantierna, inklusive format- kontra kit-version.
2. Implementera ett kombinerat pakettest över obligatoriska profiler med manipulations- och okänd profil-kontroller.
3. Kör slutlig build/test mot release-taggen och uppdatera status och release notes.
4. Ändra först därefter releasebeslutet till GO, om samtliga krav är PASS.

**Beslutet ändras inte till GO enbart för att PR #90 hade gröna tester.**

Maskinläsbar grund: `conformance/mmp-11-limited-release-decision.json`.
