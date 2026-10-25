# Skapa releasekandidattagg från telefonen

Det manuella GitHub Actions-flödet `Create release candidate tag` skapar en **lättviktig Git-tagg**, exempelvis `v1.4.0-rc.1`, vid den aktuella committen på `main`. Flödet publicerar **ingen release**.

Öppna **Actions** i GitHub, välj `Create release candidate tag`, välj **Run workflow**, välj grenen **main** och ange taggen. Körningen avbryts om taggen redan finns, namnet inte följer `vX.Y.Z-rc.N` eller `main` har flyttats sedan starten. Inga befintliga taggar flyttas eller ersätts.

Efteråt kan du kontrollera att taggen finns och starta den separata verifieringen `MMP 1.1 tagged candidate verification` med den skapade taggen som vald ref. Den publicerar inte heller någon release. Publicering är ett separat, senare beslut.
