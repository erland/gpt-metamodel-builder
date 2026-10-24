# MMP v1 – acceptansläge inför release

Datum: 2026-10-24. Status: **PARTIAL** tills publicerade runtimepaket och externa mottagare har testats.

| Ursprungligt acceptanskrav | Status | Automatiserad evidens och begränsning |
| --- | --- | --- |
| 1. Manifest, säkra relativa sökvägar | PASS i CI | test_mmp_manifest_contract.py, test_mmp_import.py |
| 2. Sju YAML och scheman offline | PASS i CI | test_mmp_export.py, test_mmp_import.py, test_mmp_interop.py |
| 3. SHA-256 och strikt inventering | PASS i CI | test_mmp_import.py, test_mmp_consumer_security.py |
| 4. ID, arv, relationer och referenser | PARTIAL | test_mmp_consumer_semantics.py täcker centrala invarianten, inte alla semantiska regler |
| 5. Typer, properties, kardinalitet | PARTIAL | Referenskonsument läser typer, egenskaper och endpoints, men inte alla uttryckligt rapporterade kardinalitetskontroller |
| 6. Modell- och formatidentitet | PASS i CI | test_mmp_interop.py, test_mmp_import.py |
| 7. Icke körbara regler redovisas | PARTIAL | Referenskonsumenten markerar regler som not_supported; regelprofilen är inte komplett definierad |
| 8. Manipulation, traversal och felaktiga referenser | PASS för testade fall | test_mmp_consumer_security.py, test_mmp_import.py |
| 9. Namnändring kontra typidentitet | NOT TESTED | Kräver explicit konsumenttest av stabil namespace+ID kontra visningsnamn |
| 10. Oberoende referenskonsument | PASS i CI | interop/mmp_v1_consumer.py och test_mmp_interop.py; inget fristående externt verktyg testat |

## Distributionskrav

Skill `metamodellering` deklarerar både `scripts/export_mmp.py` och `scripts/import_mmp.py`. Direkt exekvering av medföljande skript ska provas först. Separat versionsmatchad Engine ZIP begärs **bara** när runtime inte kan köra dessa skript. En Engine är inte ett MMP-paket.

Den portabla Engine-självtesten kör nu både domänmodellens befintliga tester och MMP:s export, import, säkerhetskontroller samt den oberoende referenskonsumenten efter uppackning av Engine ZIP.

## Kvarstående releasegates

1. Verifiera byggda Plugin-/Claude Skills-/OpenCode-paket för faktisk filnärvaro och exekvering där det stöds.
2. Testa namnbyte med oförändrat stabilt ID samt separat byte av namespace.
3. Redovisa semantiska regelbegränsningar och eventuella konsumentspecifika unsupported-features.
4. Genomför oberoende användaracceptans mot publicerad Engine ZIP och en ny canonical modell.
5. Ingen Sparx EA-import eller extern analysapplikationsintegration får rapporteras som PASS utifrån enbart MMP-testning.

Denna matris är en **spårbar testinventering**, inte ett påstående om full MMP v1-kompatibilitet.
