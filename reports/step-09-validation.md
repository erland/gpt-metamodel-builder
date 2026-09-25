# Steg 9 – valideringsrapport

Status: **PASS**

## Levererat
- deterministisk semantisk diff mellan två canonical modeller
- klassning: breaking / potentially_breaking / non_breaking
- SemVer-rekommendation och kontroll av deklarerad versionshöjning
- maskinläsbar JSON-rapport
- generering av release notes
- generering av migrationsnoteringar
- regressionstest för additiv minor-release
- regressionstest för breaking major-release
- negativt test som stoppar otillräcklig versionshöjning

## Designbeslut
Diffen använder stabila canonical ID:n som identitet. Namnändringar med bibehållet ID är därför inte strukturellt breaking, medan borttagning eller endpoint-/typändringar kan vara breaking. Komplexa constraints och viewpoint-förändringar klassas konservativt som potentiellt breaking.
