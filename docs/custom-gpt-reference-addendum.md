# Custom GPT – kompletterande referens

## Källbaserad anpassning

En extern standard eller användarlevererad metamodell normaliseras till ett source catalog och ett granskningsbart adaptation plan. Canonical output skapas först från en godkänd plan. Härledda element och relationer ska bära provenance.

## Versionshantering

Semantisk diff skiljer mellan breaking, potentially breaking och non-breaking förändringar. Borttagna typer, ändrade relation-endpoints, skärpta obligatoriska properties och borttagna enumvärden är typiska breaking changes. Versionsnivån ska vara förenlig med ändringens kompatibilitet.

## MDG-validering

Validera struktur, stereotypes/metaclasses, Tagged Values, diagram/toolbox-referenser, Quick Linker och Shape Script-payloads. XML-validering är inte samma sak som faktisk importverifiering i Enterprise Architect.

## Stateful workspace

Ett workspace håller metamodell, plattformsadapter, källor, genererade artefakter och strukturerad state separerade. `workspace-state.yaml` och ändringslogg gör projektet återupptagningsbart utan chatthistorik.
