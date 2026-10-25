# MMP Core – paketbaserad delkonformitet

Status: **utökad testtäckning**, inte full MMP Core 1.1-certifiering. MMP 1.0.0:s nio tidigare accept/reject-paket förblir separata.

`conformance/package-semantic-manifest.json` innehåller fyra extra riktiga, deterministiskt paketerade MMP ZIP-artefakter. Varje paket har omskriven kanonisk YAML, uppdaterade SHA-256-värden för varje medlem i manifestet, och egen SHA-256 i testspecifikationen.

Testfallen omfattar **positivt multipelt arv/diamantarv**, **negativ okänd property set**, **negativ okänd ärvd relationstyp**, samt **legacy-accepterad inverterad kardinalitet**. Det sista testet verifierar ett särskilt viktigt gränsfall: MMP 1.0.0:s baslinjebeteende får inte i smyg göras striktare bara för att framtida Core-semantik kan avvisa `3..1`.

Python och TypeScript läser **hela paketet** med ordinarie konsument, inte en fristående semantisk hjälpfunktion. För arv jämför båda dessutom normaliserad `effective_properties` mot samma förväntade testvärden. Detta utgör inte fullständig pakettäckning för övriga Core-regler och ger ännu inget release-godkännande för MMP 1.1.0.
