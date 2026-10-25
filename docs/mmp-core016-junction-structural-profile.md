# CORE-016 – strukturell AND/OR-junctionprofil (kandidat)

Detta är en **frivillig, fristående strukturkontroll**, inte en normativ flödesmotor eller en ändring av MMP-paketkontraktet.

En junction-definition kan ha `operator: and|or`. Denna information tolkas i nuläget endast som en känd operatörsmarkör. I instansgrafen räknas inkommande kopplingar där junction är `target` och utgående där junction är `source`. För en explicit instans kräver kandidatregeln minst en inkommande och en utgående koppling, totalt minst två. Det är ett **lokalt konstruktionsantagande** som ännu inte är godkänd generell ArchiMate-semantik.

Resultat `accept` betyder enbart strukturellt välformad enligt denna snäva kandidatregel, `reject` betyder bristande anslutning, `error` betyder felaktig referens eller instans, och `not_supported` betyder t.ex. att `complete: true` saknas eller att en känd junctiontyp saknar deklarerad AND/OR-operatör. Utan extern fullständighetsgaranti bevisar `complete: true` inte att data är kompletta.

**Ej implementerat:** AND/OR-villkor för aktivering, förgrening och sammanfogning; kantspecifika riktningar, flödes-/tokenregler, transitive effekter, junctioncykler och normativa ArchiMate-regler. Shared vectors testas av fristående Python/TypeScript-implementationer men gör inte dessa begränsningar verifierade.

Canonical YAML och MMP 1.0 ändras inte; befintliga modeller migreras inte. Detta utgör inte stöd för att publicera MMP 1.1 stable (**PARTIAL / NO-GO**).
