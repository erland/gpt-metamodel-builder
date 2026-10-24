# MMP Core – relationsarv och ändpunktskardinalitet (profilutkast)

Status: **beslutsförslag**, inte normativt publicerat MMP 1.1 och inte en förändring av MMP 1.0.0-import.

## Kandidatregel

En specialiserad relation bör endast få **försnäva** föräldrarelationens typmängder vid respektive ändpunkt: varje deklarerad undertyp ska vara samma typ som, eller transitiv undertyp av, minst en tillåten föräldratyp. Endpoint-kardinalitetens antalintervall får endast försnävas, inte vidgas. Ändrad `directed` är inte en kompatibel specialisering. `source` och `target` är även fortsättningsvis skilda roller.

## Konservativ status

- `compatible`: entydig specialisering där endpoint-typer och explicit kardinalitet inte vidgas.
- `breaking`: ändrad riktning, vidgad endpoint-typmängd eller kardinalitetsintervall.
- `needs_review`: multipla relationstypsföräldrar eller enbart en av två relaterade kardinaliteter anges. Ingen implicit kardinalitet antas.
- `invalid`: semantiskt inverterad kardinalitet eller okänd relationstypsförälder.

Detta är en **kandidatpolicy för statisk metamodell-specialisering**. Den bevisar inte att befintliga relationsinstanser kan migreras; framför allt kan striktare minimum bryta befintliga data trots att specialiseringen är tillåten i en modellhierarki. Relationers ändpunktskardinalitet behöver separata instanstester innan MMP 1.1 kan kallas färdig.

Maskinläsbara testvektorer finns i `interop/relationship-inheritance-v1.json`, körs i Python och TypeScript och inkluderas i specifikationspaketet. Någon strikt gate för befintliga MMP 1.0.0-paket införs inte.
