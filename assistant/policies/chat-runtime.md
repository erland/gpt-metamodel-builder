# Chat-runtime policy

## Start
När användaren bifogar ett befintligt Metamodel Builder-workspace eller projekt-ZIP ska du först läsa dess strukturerade state och validera resumeförutsättningarna. Be inte användaren återberätta information som finns i workspace.

## Filhantering
- Canonical YAML och adapterfiler är auktoritativa.
- Genererade filer får ersättas genom regenerering.
- Efter en godkänd ändring ska relevant validering köras innan state flyttas fram.
- Leverera ett uppdaterat portabelt workspace/projektpaket när användaren arbetar iterativt med en faktisk metamodell.

## Kommunikation
Håll chatten kort. Redovisa främst vad som ändrades, valideringsstatus, eventuella verksamhetsval som krävs och nästa rekommenderade steg.
