# Biome load round — decision strings, written BEFORE launch 2026-09-25 (BENCH)

Batch: loadsweep BASE-9 + 15 extras (`src/RimMandrake/Utils/loadsweep/biome_round_batch.txt`)
= 24 mods. Purpose: prove the 8 new RM_ biome mods load clean (step 5 of their build items).
Eight new assemblies ride this load under the standing name-attribution waiver — one
signature each, below, written before the log exists.

## Per-assembly failure signatures (any hit = that mod fails, others unaffected)
- `TypeLoadException`/`ReflectionTypeLoadException` naming `RimMandrake.TheRot`
- … naming `RimMandrake.FeverWood`
- … naming `RimMandrake.TerminalBiomes`
- … naming `RimMandrake.Greentide`
- … naming `RimMandrake.NightsideIce`
- … naming `RimMandrake.Stillsand`
- … naming `RimMandrake.LongShade`
- … naming `RimMandrake.Wasteland`

## FAIL strings (whole batch)
- `Recovered from incompatible or corrupted mods` or `Caught exception while loading play data`
- disk activeMods collapses to 6 (recovery reset)
- `^Config error in` naming any `RM_` def
- `Could not resolve cross-reference` naming `RM_`
- `Patch operation` + `failed` naming a mandrake file

## PASS positive (not silence)
- `Bridge token:` present; disk_active_mods = 24
- `jawa/get_defs` non-null for every sentinel:
  BiomeDef: RM_TheRot · RM_FeverWood · RM_Greentide · RM_NightsideIce · RM_Stillsand ·
  RM_LongShade · RM_Wasteland · RM_TheScald · RM_GreySea · RM_TwilightSea · RM_PropaneLake
  ThingDef: RM_Vaunoom (VWake reconciliation) · RM_Fessk (cast wiring) · RM_Eesh (fish
  retier) · RM_Vorrel (LongShade move) · RM_GiantLeaf (FeverWood Q13 dup)
  TerrainDef: RM_TheRotGrass (TheRot own ground) · RM_SolidPropane (PropaneLake own terrain)
- KNOWN-ACCEPTED, not failures: Wasteland's unguarded `VolcanoSoil`/`WastelandAsphalt`
  terrainsByFertility resolve only because sarg.alphabiomes is in this batch — its true
  standalone gap stays open on WASTELAND_RM_MOD_BUILD_1. Missing real art renders
  placeholder silhouettes; pink squares on RM_DosimeterLawn/RM_VaultRoot (texPaths with no
  PNG) are a recorded LongShade/Wasteland robustness-pass item, not a load failure.
