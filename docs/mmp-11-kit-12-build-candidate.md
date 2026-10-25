# Separat Specification Kit 1.2.0 – MMP 1.1 kandidat

Det befintliga Specification Kit **1.1.0** innehåller fortfarande stabilt MMP-format **1.0.0** och byggs helt oförändrat.

Det nya skriptet `scripts/build_mmp_specification_1_2.py` skapar en **separat** `mmp-specification-kit-1.2.0.zip`, vars metadata anger kandidatformat **1.1.0**. Distributionen återanvänder baslinjens conformancepaket och kompletterar med nuvarande 1.1-kontraktsdokument, profiler, scheman och testunderlag. Äldre medföljande specifikationsdokument hänvisar fortfarande till 1.0-baslinjen och får inte uppfattas som en komplett normativ 1.1-specifikation.

`python scripts/test_mmp_specification_1_2.py` bygger kitet två gånger, jämför byteidentitet och kontrollerar samtliga SHA-256-poster och versionsmetadata.

**Avgränsning:** Detta är en releasekandidat för kitbyggnaden, inte publicering, verifierad release från en tagg eller ett GO-beslut om full MMP 1.1-konformitet. Ett nytt versionsanpassat README, konsoliderad releaseinformation och taggbunden slutgrind återstår. Befintligt kit ändras inte.
