# MMP 1.0.0 -> föreslagen 1.1: kompatibilitetsanalys

Detta är en **beslutsmatris**, inte utgiven 1.1-specifikation. Utgångspunkt: publicerade 1.0.0-scheman och dokument. Kodändringar skjuts upp till efter beslut.

| Förtydligande | Stöd i publicerade 1.0.0-scheman | Risk | Planerad hantering |
| --- | --- | --- | --- |
| Cykelfritt arv och kända extends-referenser | Schemat definierar referenslistor men inte full grafsemantik | Vissa schema-giltiga paket kan avvisas | Kräv i opt-in Core-strikt profil; inför inte tyst ny regel för alla 1.0.0-konsumenter |
| Deduplicerad egenskap via gemensamt property-ID | Samma globala definition refereras via property_sets | Semantik hittills underförstådd | Dokumentera som semantisk precisering, test med diamant-arv |
| Konflikter mellan grupper och egenskaps-ID | Global egenskapsdefinitionslista utan överlagring | Störst risk vid verktygens etikettbaserade deduplicering | ID-baserad union; inga namn-baserade sammanslagningar |
| Element/relations-id och abstrakta typer | `abstract`, `extends`, `source/target` och `directed` finns | Konsumenter kan tolka instansregler olika | Precisera riktning; lägg gränsöverskridande testfall |
| Kardinalitet | `common-definitions` tillåter `*`, heltal, `n..m`, `n..*` | Syntax tillåter semantiskt inverterade intervall | Semantiskt `min<=max` i framtida strikt profil |
| `required` och `cardinality` | Båda tillåtna samtidigt | Motstridiga minvärden är möjliga | Definiera prioritet endast efter explicit beslut; preliminärt avvisa i strict profile |
| `default` mot datatype | `default: {}` i JSON Schema = valfritt värde | Kan avvisa tidigare giltiga 1.0.0-paket | Inför opt-in validering eller framtida major-ändring |
| Regeluttryck och språk | Fyra language-etiketter utan exekverbar semantik | Ogiltiga PASS-påståenden | Bevara text och rapportera `not_supported` om profil saknas |
| Versionsdiff | Modellversion och breaking-klassning finns | Felaktigt safe-kompatibilitetsbeslut | Definiera versioneringspolicy med `needs_review` där påverkan är okänd |
| Namnrymdssatta extensions | extensions finns men criticality inte reglerad | Okänd semantik kan ignoreras felaktigt | Förhandla separat profil, inte ändra gamla extensions retroaktivt |

## Kontrollprincip

Vårt mål är inte att alla tidigare JSON Schema-giltiga paket automatiskt måste klara en framtida strikt profil. Däremot ska de förbli **igenkännbara som MMP 1.0.0** och en 1.0.0-konsument får inte omtolka dem enligt ännu inte publicerade 1.1-regler.

**Beslut före implementation:** fastställ vilka preciseringar som är dokumenterande, vilka som kräver opt-in konformitetsprofil och vilka som faktiskt är brytande. Om innebörden av ett redan accepterat fält behöver ändras krävs en större formatversion.

Se `mmp-core-semantics-proposal.md` för den fullständiga semantiska texten.
