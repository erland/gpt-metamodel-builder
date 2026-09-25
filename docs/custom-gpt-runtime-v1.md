# ChatGPT Custom runtime v1

Custom GPT-distributionen kompileras från samma canonical projekt som Chat och OpenCode. Kärninstruktionen kompletteras med det stateful workflow som annars ligger i separat policy, så kritiskt beteende inte är beroende av Knowledge.

## Knowledge-strategi

Builder-paketet innehåller högst 20 prioriterade referensfiler. De består av teknisk metamodell-/Sparx-referens och Architecture Lite-exempel. Knowledge är referensmaterial; beteenderegler ligger i den kompilerade instruktionen.

## Capability

Rekommenderade Builder-funktioner är Web Search och Data Analysis/Code Interpreter. Bildgenerering behövs inte. Filuppladdning krävs för stateful import/export.

## Paritet

Kärnuppgifterna kan utföras i Custom GPT, men lokala projektscript är inte inbäddade exekverbara verktyg. Exakt deterministisk scriptparitet med Chat/OpenCode är därför reducerad. GPT:n ska använda Data Analysis när möjligt och aldrig rapportera en kontroll som körd om den inte faktiskt körts.
