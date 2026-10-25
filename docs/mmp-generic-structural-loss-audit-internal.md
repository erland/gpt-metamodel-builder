# Intern strukturell inventering och förlustkontroll

Den syntetiska stor-fixturen används för att verifiera **informationsbevarande i kandidatpaket**, inte för att distribuera en modelleringsspråksdefinition.

## Inventering

Varje testkörning sammanställer mängder av identifierare och innehållsdigests för element-, relations- och junctiontyper. Dessutom kontrolleras **exakta deklarerade relationspar per relationstyp**, inte bara summerade antal. Fixturebasens förväntade omfattning är 49 tillförda elementtyper, sju tillförda relationstyper, två junctiontyper och 5 047 tillförda tillåtna typade par. Befintliga grundtyper ingår också i paketets totala inventering.

## Testkedja

Skriptet `scripts/test_mmp_generic_loss_audit.py` genererar modellen, gör en MMP 1.1-kandidatexport, validerar paketet, importerar modellen och jämför hela typ- och relationsinventeringen med ursprunget. TypeScript-workflow testar dessutom konsumentens läsning av samma paket.

Två avsiktliga negativa kontrollfall bevisar att jämförelsen upptäcker (a) ändrat relationspar även när antalet par är oförändrat och (b) att en elementtyp försvinner.

Utdata är en maskinläsbar körningsrapport med antal, hashvärden och resultat; fullständig parmatris återges inte i rapporten. Rapporten är körningsresultat, inte en publicerad extern standard eller officiell kompatibilitetsförsäkran.

## Begränsningar

Testet visar syntaktiskt och deklarativt innehållsbevarande i den testade modellen. Det verifierar inte semantisk ekvivalens mellan oberoende modelleringsverktyg, fullständig instansgrafsvalidering eller generella regler för härledning. MMP 1.1 är fortfarande **PARTIAL / NO-GO**.
