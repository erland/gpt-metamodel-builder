# Standard-/källbaserad anpassning v1

## Syfte

Steg 10 inför ett tvåfasigt arbetsflöde för att härleda en egen canonical metamodell från en extern standard, modell, MDG, dokumentation eller annan användarlevererad källa.

## Normaliserad källa

Källmaterial analyseras först till `source-catalog.yaml`. Katalogen innehåller endast de begrepp och relationer som behövs för aktuell anpassning och varje post har en `reference` tillbaka till källan. Kompletta tredjepartsspecifikationer behöver därför inte distribueras i projektet.

## Tvåfasigt arbetsflöde

1. **Propose** skapar `adaptation-plan.yaml` med status `draft`.
2. GPT:n presenterar urval, namnbyten, specialiseringar och bortval kortfattat för användaren.
3. Planen ändras till `approved` först efter verksamhetsmässigt godkännande.
4. **Apply** vägrar skapa canonical output från en plan som fortfarande är `draft`.
5. Godkänd plan projiceras deterministiskt till canonical YAML.
6. Schema- och semantikvalidering körs innan modellen betraktas som giltig.

## Tillåtna actions

- `keep` – behåll källbegreppet i huvudsak oförändrat.
- `rename` – behåll semantiken men använd lokal benämning/identifierare.
- `specialize` – skapa en lokal specialisering av källbegreppet.
- `omit` – ta inte med begreppet eller relationen i målmodellen.

## Provenance

Varje skapat element och relation får en provenance-mappning med käll-ID, referens, härledningsrelation och motivering. `specialize` ger `specializes`, `keep` ger `equivalent_to` och övriga härledda varianter ger `derived_from`.

## Licensprincip

Projektet ska inte paketera hela ArchiMate-, TOGAF-, UML-, BPMN- eller andra tredjepartsspecifikationer bara för att möjliggöra anpassning. Använd tillåtna källor, användarens eget material eller normaliserade utdrag och bevara referens/provenance.

## Begränsning v1

Deterministiska scripts tolkar inte godtycklig standardtext automatiskt. GPT:n ansvarar för källanalys och normalisering; scripts ansvarar för schema, godkännandegate, deterministisk projektion och validering. Den separationen gör tolkningen granskningsbar och framtida parsers kan läggas till utan att ändra canonical modellen.
