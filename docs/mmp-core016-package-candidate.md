# CORE-016 – MMP 1.1-kandidat med typade ändpunkter

CORE-016 kan nu anges som en **obligatorisk kapabilitet** i både canonical metamodel och MMP 1.1-kandidatmanifest:

```yaml
metamodel:
  extensions:
    mmp_required_capabilities:
      - id: mmp-typed-endpoints
        version: 1.0.0
```

Exportflaggan `--candidate-1-1` krävs om modellen innehåller `junctions` eller `typed_refs`. MMP 1.0-export avvisas före skrivning. Importör och oberoende Python/TypeScript-konsumenter kräver samma kapabilitetsdeklaration i integritetskontrollerat manifest och canonical YAML, verifierar typade referenser mot element-, relations- respektive junction-ID, förbjuder dubletter och kräver att äldre `types` motsvarar elementdelen av `typed_refs`.

## Migration
Gammal YAML utan `typed_refs` eller `junctions` behöver inte migreras. Ingen automatisk omskrivning sker. Ny modell exporteras till ett nytt paket och importeras till en ny arbetsyta. Äldre MMP 1.0 med nya CORE-016-fält avvisas även om manifest skulle manipuleras till att ange 1.0.

## Pakettester
`scripts/test_mmp_typed_endpoints_package.py` bygger ett MMP 1.1-kandidatpaket med en relation till en relation, en junction och elementreferenser. Den kontrollerar 1.0-avvisning, 1.1-export, import/bytebevarande, explicit kapabilitetskrav och att båda konsumenterna accepterar testpaketet. CI och TypeScript-workflow inkluderar testet.

## Begränsningar
**CORE-016 är PARTIAL, MMP 1.1 NO-GO.** Denna etapp verifierar statiska typade referenser, inte den fullständiga junctionsemantiken eller typade pairwise-regler/instrumenterad instansvalidering. Avancerat arv och sambandet med CORE-015:s `allowed_type_pairs` måste fortfarande definieras och testas.
