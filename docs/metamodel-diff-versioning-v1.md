# Metamodell-diff och versionshantering v1

Steg 9 inför en deterministisk semantisk diff mellan två canonical metamodellkataloger.

## Klassning

Ändringar klassas som `breaking`, `potentially_breaking` eller `non_breaking`. Exempel på breaking changes är borttagna element/relationer, ändrad relationriktning eller endpoints, ändrad property-typ, borttaget enum-värde och egenskaper som blir obligatoriska. Nya typer är normalt icke-breaking. Viewpoint-, constraint-, arv- och property-set-förändringar behandlas konservativt som potentiellt breaking.

## Versionering

Verktyget rekommenderar SemVer-höjning:

- breaking ändring → major
- additiv eller potentiellt breaking ändring → minor
- endast icke-breaking metadata/presentationsändring → patch

En deklarerad version som är lägre än miniminivån gör diff-kommandot felmarkerat.

## Artefakter

`diff_metamodel.py` kan generera:

- maskinläsbar JSON-diff
- Markdown release notes
- Markdown migrationsnoteringar

Diffen utgår från stabila canonical ID:n. Ett namnbyte med bibehållet ID behandlas därför som presentations-/metadataändring, medan borttagning och återintroduktion med nytt ID blir en strukturell ändring.
