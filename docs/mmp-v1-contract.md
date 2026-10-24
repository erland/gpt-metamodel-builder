# Metamodel Exchange Package (MMP) v1 – kontrakt

Status: publicerat projektspecifikt format, inte extern standard. Version på paketkontraktet: `1.0.0`. **Kommande semantiska preciseringar** dokumenteras separat i [MMP Core-förslaget](mmp-core-semantics-proposal.md) och [kompatibilitetsanalysen](mmp-core-compatibility-analysis.md); dessa ändrar inte retroaktivt gällande 1.0.0.

MMP är ett generellt, självbeskrivande utbytespaket **för metamodell**, inte för instansdata eller verktygsspecifik konfiguration. Befintlig canonical YAML är sanningskälla; MMP är en distributionsprojektion och en inläst MMP får inte ändra originalpaketet.

## Normativt innehåll

Paketet kan vara en ZIP (`.mmp.zip`) eller en katalog med samma rot. Roten har `manifest.yaml`, `canonical/`, `schemas/` och valfritt `documentation/`. Exakt filplacering bestäms av manifestet, inte av hårdkodade konsumentsökvägar.

Sju obligatoriska canonical entrypoints: `metamodel`, `properties`, `constraints`, `viewpoints`, `notation`, `provenance`, `version`. Alla filer refereras i `manifest.entrypoints` med relativa sökvägar. `guidance` är **valfri** åttonde entrypoint; exportera den när den finns. Metamodel Builders interna validering kräver i dag `guidance.yaml`; importören får skapa den från en definierad, versionslåst standardmall i en **ny** projektarbetsyta, utan att skriva till paketet. Det är ingen obligatorisk MMP-resurs.

Samtliga schemafiler som behövs för lokal JSON Schema-validering, inklusive indirekta `$ref`, måste medfölja under `schemas/`. För de sju canonical-filerna finns minst sju motsvarande JSON Schemas och `common-definitions.schema.json`. Schema-id får vara URI-identifikatorer; lokal inläsning får inte hämta externa resurser.

Manifestet valideras mot `schemas/mmp-manifest-v1.schema.json` (detta repo). I ett distribuerat MMP-paket behöver detta *manifest-schema* inte ingå, men alla **canonical JSON Schemas** måste ingå.

## Identitet och kompatibilitet

`package_format: mmp`; `package_format_version: 1.0.0`. `metamodel.id`, `metamodel.version` och `metamodel.namespace` är obligatoriska i manifestet. Modellen identifieras globalt med en stabil namnrymd och lokala ID:n. URI-namnrymden behöver inte vara uppslagsbar. Typidentiteten i v1 är `<namespace>#<percent-encoded-local-id>`, med UTF-8 RFC 3986 percent-encoding för lokal-ID:t. Identifierarens namn/etikett får ändras utan byte av typidentitet; byte av namespace är däremot en explicit identitetsändring.

MMP-exporten **kräver** en stabil `metamodel.namespace`. Om modellen saknar den måste användaren godkänna ett permanent värde som skrivs till canonical källan via normal modelländringsprocess **före** export; exportören får aldrig generera slumpmässiga namnrymder. `manifest.metamodel.id/version` ska vara samma som `metamodel.yaml:metamodel.id/version`, och `version.yaml:version.current` ska vara identisk.

MMP-formatmajor annat än 1 avvisas. Minor/patch tillåts endast om okända frivilliga fält kan ignoreras utan att semantiken ändras. Producentens valfria valideringsstatus är inte konsumentens valideringsbevis.

## Manifest och säkerhet

Manifestet innehåller `producer.name/version`, UTC `generated_at`, `entrypoints`, och `files` där varje fil **utom manifestet** finns exakt en gång med `path`, `role`, `media_type` och SHA-256 i gemener. Manifestet ingår aldrig i sin egen hashlista.

Strikt import avvisar ej deklarerade filer, duplicerade poster eller sökvägar, symlänkar, traversal (`..`), absoluta vägar och `\\`. Definiera även gränser för filantal, total uppackad storlek, enskild filstorlek och kompressionskvot innan ZIP läses in. Kontrollera alla hashar före YAML- och schema-parsning. Säker YAML-parser (`safe_load`) och endast lokala schema-referenser ska användas. MMP-import kör **aldrig** medföljande exekverbar kod.

Validering har tre separata nivåer: (1) paket/manifest/SHA, (2) struktur mot medföljande JSON Schemas och (3) canonical semantik/versionskonsistens. Constraints som inte kan utvärderas ska redovisas som `not_supported` eller `not_applicable`, aldrig som implicit `passed`. Generatortid `generated_at` bör respektera `SOURCE_DATE_EPOCH` för reproducerbar export.

## Separation mot andra artefakter

Ingen instansdata, Excel-kolumnmappning, Sparx-adapter, exekverbar kod eller hemlighet får ingå i MMP-kärnformatet. Sparx MDG och eventuellt Ecore/XMI förblir separata, valfria projektioner.

## Första implementationen (kommande PR:ar)

1. Export av ZIP och katalog med checksummor, versionslåsning och offline-schemaresurser.
2. Säker importör med lägena `inspect`, `validate`, `import`, konfliktpolicy utan tyst överskrivning.
3. Oberoende referenskonsument samt positiva, negativa, roundtrip- och korruptionstester.
4. Skill-, runtime- och Engine-integrering; inbyggda skript körs i första hand, Engine ZIP bara när exekveringsmiljö saknas.

Ett MMP-paket är **inte** Metamodel Builders Engine ZIP: motorn innehåller körbara verktyg, MMP innehåller enbart deklarativ metamodell och valideringsresurser.

## Föreslagna konformitetsprofiler

Nästa formatrevision behandlas i [MMP-konformitetsprofilerna](mmp-conformance-profiles-proposal.md). Deklarationsformatet finns i `schemas/mmp-conformance-declaration-v1.schema.json` och ska användas utanför befintliga 1.0.0-manifest.
