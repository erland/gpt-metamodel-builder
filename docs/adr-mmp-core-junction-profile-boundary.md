# ADR – MMP Core kontra junction-semantik

Datum: 2026-10-25. Beslut: **behåll typade junction-referenser i Core; lägg operatorbunden strukturell och beteendemässig junction-semantik i separata profiler.** MMP 1.1 är alltjämt PARTIAL/NO-GO.

## Bakgrund

CORE-016 har redan generella junction-typer (`junctions[].id/name`), typade endpoints (`kind: junction`) och validering av referenser och explicita instanskopplingar. PR #73 tillförde en separat frivillig kandidatkontroll för anslutningar, med `operator: and|or` som en fältförutsättning i testmodellen. Detta fält **finns inte i det kanoniska Core-schemat** (`junctionType` avvisar okända fält). Vi ska därför inte göra det till ett implicit Core-krav eller hävda att denna information redan kan roundtrippas i ett MMP-paket.

## Beslut och kontraktsgränser

1. **Core:** ID, namn och referensintegritet för junction-typer; typade referenser i relationernas ändpunkter och deklarativa tillåtna typade par. Core beskriver struktur utan krav på AND/OR-aktivering.
2. **Separat kandidatprofil:** `mmp-junction-structure@0.1.0` har eget, isolerat JSON-schema: `schemas/mmp-junction-structure-profile.schema.json`. Det mappar junction-typ-ID till `and` eller `or` via `junction_operators`. Profilen är ännu **inte paketerad, versionsförhandlad eller deklarerad som stödd av MMP-konsumenterna**.
3. **Strukturell grafprövning:** befintliga `scripts/mmp_junction_structure.py` och TypeScript-golden-test mäter in-/utgrad enligt en **lokal kandidatregel**, inte normativ generell junction-semantik.
4. **Beteende:** aktivering, AND/OR-villkor, tokens, flödesriktning, sammanfogning, split, topologiska cykler och transitive effekter ingår inte i Core eller i den fastställda strukturella kandidaten.

## Bakåtkompatibilitet och acceptanskriterier

- Scheman för canonical YAML och publicerad MMP 1.0 ändras inte, och äldre modeller migreras inte.
- Odeklarerad operator medför ingen förmodad AND eller OR. Avsaknad av profilstöd ska redovisas som `not_supported`; inte falla tillbaka till tyst godkännande.
- CI-testet `scripts/test_mmp_junction_profile_boundary.py` kontrollerar att profilformatet är giltigt, att okända operatorer/extra fält avvisas och att Core-junctionschemat fortsatt saknar operatorfältet.
- **Detta är en gränsdragnings-PR**, inte ett bevis på interoperabilitet eller att profilen är aktiv i export/import.

## Föreslaget nästa utvecklingssteg

Koppla kandidatprofilen explicit till MMP 1.1:s tilläggs- och kapabilitetsförhandling, definiera en separat paketdokument-/extensions-plats, och anpassa Python/TypeScript-grafprövning att läsa samma isolerade profilformat. Före aktivering ska negativa fall för saknad, okänd och inkonsistent profil testas fail-closed. Utför inte automatisk konvertering av gamla junction-definitioner.
