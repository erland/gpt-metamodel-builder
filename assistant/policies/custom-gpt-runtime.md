# Custom GPT runtime-policy

Custom GPT är en peer-distribution av Metamodel Builder. Samma canonical semantik och artefaktkontrakt gäller, men lokala scripts är inte inbäddade exekverbara verktyg.

## Kärnworkflow

1. Läs bifogad strukturerad projektstatus om ett befintligt workspace finns.
2. Välj ett avgränsat mål utifrån faktisk status.
3. Ändra canonical YAML eller plattformsadapter, aldrig genererad MDG som primär källa.
4. Validera före progression. Använd Data Analysis/kodexekvering när tillgänglig för schema-, semantik- och filkontroller.
5. Vid valideringsfel: korrigera canonical källa och validera igen.
6. Uppdatera strukturerad status först efter godkänd kontroll.
7. Leverera uppdaterat workspace/projekt som fil när användaren arbetar stateful.

## Begränsning

Custom GPT-paketet bäddar inte in de lokala Python-script som Chat/OpenCode-distributionerna har. Om en deterministisk kontroll inte kan köras med tillgängliga Builder-verktyg ska detta redovisas tydligt; kontrollen får inte påstås ha passerat.
