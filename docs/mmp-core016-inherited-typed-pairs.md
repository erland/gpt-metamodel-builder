# CORE-015/016 – ärvda exakta typade relationspar (kandidat)

En relationstyp kan ärva `allowed_typed_pairs` från en eller flera föräldrar. I denna **frivilliga analysfunktion** tillför varje explicit parlista en begränsning, och effektiva par definieras som **snittet** av samtliga föräldrars och barnets deklarerade parlistor. Multipelt arv **utvidgar aldrig** det tillåtna antalet kombinationer.

Typade nycklar matchas exakt på `{kind,id}`. Ingen implicit utvidgning över element-, relations- eller junction-subtyper sker i denna etapp. Barnets deklarerade `source.typed_refs` och `target.typed_refs` filtrerar dessutom resultatet. Tomt snitt, okända referenser, cykliskt typ-arv och otillåtna kombinationer avvisas. Saknat par-kontrakt hos en förälder avvisas `not_supported`, så att en äldre relationstyp inte tyst ger rätt till nya par.

Implementation: `scripts/mmp_effective_typed_pairs.py`. Gemensamma positiva/negativa referensfall: `interop/core016-inherited-typed-pairs-v1.json`, verifierade separat i Python och TypeScript.

**Avgränsning:** Funktionen läser metamodelldata och är inte ännu inkopplad i MMP-paketvalideringen eller instansgrafsvalideringen. Det är avsiktligt: här fastställs först snittsemantiken. MMP 1.0, canonical YAML och befintliga profiler ändras inte. Ingen automatisk migrering, och MMP 1.1 förblir **PARTIAL / NO-GO**.

Nästa steg är att explicit koppla denna beräkning till paketkonsumenternas förhandlade profil och valideringen av verkliga instanskanter, utan tysta arvsgissningar.
