# CORE-016 – canonical typade ändpunkter (etapp 1)

Status: **PARTIAL**. Endast canonical schema och validator. MMP 1.1 förblir NO-GO.

## Generell representation

I `metamodel.yaml` är `junctions` en valfri samling av namngivna och identifierade junction-typer. En relations `source` eller `target` får valfritt ange `typed_refs` med objekt `{kind, id}`; `kind` är en av `element`, `relationship`, `junction`. Befintligt `types` fortsätter vara obligatoriskt (och får vara tomt), med enbart elementreferenser.

Exempel:
```yaml
junctions:
  - id: and_junction
    name: AND
relationships:
  - id: dependency
    name: Dependency
    source:
      types: [application_component]
      typed_refs:
        - kind: element
          id: application_component
        - kind: junction
          id: and_junction
    target:
      types: []
      typed_refs:
        - kind: relationship
          id: dependency
```

När `typed_refs` finns måste alla elementreferenser i listan **exakt** motsvara `types`. Detta dubbla fält är en avsiktlig migrationsbrygga, inte två konkurrerande sanningskällor. Validatorn avvisar okända typade referenser, dubbletter, namespace-kollisioner och inkonsekvens mellan elementdelen och legacy-fältet.

## Migreringsstrategi

Gammal canonical YAML utan `junctions` och `typed_refs` förblir giltig utan ändring. Inga automatiska migreringsskript behövs för att läsa den. En framtida frivillig konvertering kan skapa `typed_refs` av befintliga `types` med `kind: element` i en **ny kopia**; denna PR genomför ingen konvertering och skriver inte om äldre YAML.

Inget MMP 1.0- eller 1.1-kandidatpaket med dessa nya egenskaper får exporteras innan CORE-016:s profil är förhandlingsbar och konsumenterna verifierar dess semantik; exporten avvisar därför modellen före paketskrivning.

## Kvarstående arbete

Denna etapp innebär inte att vi redan har fullständigt stöd för relationer till relationer eller junctions i externa konsumenter, i pairwise-normalisering eller vid instansvalidering. Nästa steg är explicit kapabilitetsprofil, MMP-schema-/manifestförhandling, Python/TypeScript-paritet och end-to-end-test med typade ändpunkter. Relationstypsarv och `allowed_type_pairs` för andra ändpunktskategorier kräver också särskilda semantikbeslut.
