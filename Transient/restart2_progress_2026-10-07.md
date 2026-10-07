# Full restart #2, 2026-10-07 (GSS into full list + Kinetic Arms/GSS live checks)

- 03:48 start; bridge held by BENCH
- 03:58 game was already gone (a 34-mod instance had started ~03:5x and exited); FOUNDRY deployed Greentide/Stillsand/CreatureBehaviors meanwhile (23550555d)
- 04:02 pulled to 23550555d; deployed 16+1 files (GSS DLL, StructureInjectionsSW + UtinniPatches fall-line wrecks) + Biomes 15 files (Abyss/FeverWood/RustCathedral/Warscar DLLs, Bileworm). Abyss, Stillsand, CreatureBehaviors, GSS, KineticArms, ExplosiveKnockback DLLs md5-match the repo
- 04:05 ModsConfig = FULL.LATEST 610 + explosiveknockback, kineticarms, gimmesomeslack after flowworks = 613 (ET parse, 6 Ludeon); snapshot infrastructure/state/modlists/ModsConfig.FULL_plus_EK_KA_GSS_2026-10-07.xml
- 04:05 launched via steam.exe -applaunch 294100
- 04:08 my 613-mod load was killed mid-load and ModsConfig swapped to a 34-mod tier at 04:09:09 by a FOUNDRY modcheck run (LeaningScrub/WeepingStones) that did not take the bridge; FOUNDRY game PID 108028 now up. Waiting for it to finish rather than fight
- 04:26 FOUNDRY's tier game exited; 613 list rewritten; relaunched via Steam (PID 148624)
