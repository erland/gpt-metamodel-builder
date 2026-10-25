# CORE-016 – förhandlad junction-profil i MMP 1.1-kandidat

Ny obligatorisk kandidatkapabilitet: `mmp-junction-structure@0.1.0`. Den ska uttryckligen listas i `metamodel.extensions.mmp_required_capabilities`; dessutom kräver paket med junctions `mmp-typed-endpoints@1.0.0`.

En modell kan tillhandahålla **en separat profilfil** `profiles/junction-structure.json` med exempel:

```json
{"profile":"mmp-junction-structure@0.1.0","junction_operators":{"j1":"and"}}
```

Exportören placerar oförändrade byte i `documentation/junction-structure.json`, bäddar in offline-schema och registrerar SHA-256 i MMP-manifestet. Denna profil ska täcka exakt mängden deklarerade junction-typ-ID:n. Importör samt oberoende Python/TypeScript-konsumenter avvisar okända profiler, saknat dokument, okänd operator och inkonsistens i typ-ID:n. Denna version av profilen **transporteras och valideras**, men kör inte AND/OR-aktiveringsregler automatiskt.

**Kompatibilitet:** MMP 1.0 blockeras vid nya obligatoriska kapabiliteter; äldre canonical YAML är oförändrad, automatisk migrering saknas. Detta är ännu en kandidat, MMP 1.1 **PARTIAL/NO-GO**.