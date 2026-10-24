# MMP Conformance Profiles – förslag för MMP 1.1

Status: **förslag**, inte retroaktivt normativt för publicerade MMP 1.0.0-paket. Läs tillsammans med `mmp-core-semantics-proposal.md` och `mmp-core-compatibility-analysis.md`.

## Modell: nivåer och roller

Konformitet är en egenskap hos en **implementation** (till exempel en read-only-konsument eller en producent), inte en garanti som följer av paketets `validation`-fält. En konsument deklarerar maskinläsbart sin implementation och stödjande profiler via ett separat deklarationsdokument; det ändrar **inte** `manifest.yaml` i MMP 1.0.0.

`mmp-core` är obligatorisk basprofil för framtida anspråk på MMP 1.1-konformitet; `mmp-rules`, `mmp-notation` och `mmp-viewpoints` är valfria. En profil kan rapporteras som `supported`, `partial` eller `unsupported`. Endast `supported` får användas för fullt konformitetsanspråk. `partial` måste ange konkret begränsning i `limitations`.

### MMP Core (`mmp-core`)

Konsumenten måste korrekt:
1. Läsa MMP ZIP och katalog, kontrollera inventering, SHA-256, säkra relativa sökvägar och lokala JSON Schemas.
2. Kontrollera identitet, versionssamstämmighet, referensintegritet, unika ID och separata element-/relationstyper.
3. Hantera `abstract`, `extends`, acykliskt (även multipelt) arv och entydig union av ärvda property sets och egenskaper.
4. Tolka relationsriktning, endpoint-typer samt kardinalitet enligt specificerad profil. För de olösta frågorna i semantikförslaget måste stödet redovisas som `partial`; de får inte döljas.
5. Redovisa saknad semantisk implementation som `not_supported` snarare än godkänt resultat.

### Valfria profiler

- `mmp-rules`: Utvärdering av ett publicerat, exakt definierat regeluttrycksspråk. Läsning och bevarande av `constraints.yaml` utan utvärdering ger **inte** profilstöd. Stödda språk/profilversioner deklareras under `rule_languages`; `natural_language` är inte automatiskt exekverbart.
- `mmp-notation`: Tolkning av symbol- och presentationsdefinitioner i `notation.yaml`, utöver ren schema-/paketläsning. Stöd för en viss verktygsspecifik rendering måste redovisas separat.
- `mmp-viewpoints`: Tolkning av definierade viewpoints och begränsningar för vad en vy får innehålla, utöver ren läsning av `viewpoints.yaml`.

Alla profiler kräver Core `supported` för att ge ett fullt MMP-konformitetsanspråk. Ett verktyg får ange `partial`/ `unsupported` profiler som kapabilitetsinformation.

## Maskinläsbar declaration

Separat JSON-dokument enligt `schemas/mmp-conformance-declaration-v1.schema.json`. Se `examples/mmp-consumer-conformance.json`.

- `declaration_version` anger format på kapabilitetsdeklarationen, inte MMP-paketets version.
- `implementation` innehåller produktnamn och version samt rollen `consumer`, `producer` eller `both`.
- `package_format_versions` är de versioner konsumenten uppger stöd för; detta är ingen automatisk versionsförhandling.
- `profiles` innehåller explicita statuser och eventuella begränsningar; alla fyra profiler måste listas.
- `rule_languages` är en lista med identifierare för faktiskt implementerade språk/profiler, inte en indikation på att fri regeltext kan exekveras.

Deklarationen ska inte placeras inuti 1.0.0-paketets `manifest.yaml`, eftersom dess `additionalProperties: false` då skulle ogiltigförklara manifestet.

## Validering och verifierbarhet

En deklaration som passar JSON Schema bevisar **endast korrekt deklarationsstruktur**. En framtida gemensam conformance suite måste verifiera varje fullt stödd profil med positiva och negativa testpaket och ge ett testprotokoll med `pass`, `fail`, `not_supported` eller `not_applicable` per testfall.

En okänd profil eller okänd regelprofil får inte tyst räknas som `supported`. Frånvaro av runtime-test i en verklig host är inte liktydigt med PASS.

## Versionspolicy

Detta är ett förslag inför MMP 1.1, inte en utökning av publicerade MMP 1.0.0-manifest. Om Core-strikt semantik avvisar tidigare accepterade 1.0.0-konstruktioner krävs frivillig strict-profil eller separat huvudversionsbeslut. Konsumenter för 1.0.0 behöver inte påstå Core 1.1-konformitet.
