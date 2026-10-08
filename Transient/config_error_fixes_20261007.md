# Config error fixes 20261007 (uncommitted, offline)

1. FIXED RM_FloodedCanyon: removed 6 franchise rows (RUT_SealedSleeper, RUT_EmperorVulture, RSW_SandLeaper, RSW_SandPillar, RSW_Creature_Mantrap, RSW_MutagenicNorphea) from
   src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml. No new patch needed: all six already ship in
   src/RimUtinni/UtinniPatches/Patches/WildAnimals_CrackedLands.xml Op 2. Free roster keeps RM_Muttavaq, RM_Uttaqar, RM_Tarruq (3 RM rows, >=2).
   Caveat: the NRE in ConfigErrors is presumed to come from the unresolved rows; unproven until a live load.
2. NOT CHANGED RM_FE_* burnedDef flammable: deliberate, owner ruled "accept" 2026-09-03 (header of src/RimMandrake/Pyrelands/Defs/TerrainDefs/ScorchableGround.xml, AshLadder.xml; "DO NOT FIX"). Design call.
3. FIXED RM_TractionLance: removed constructEffect (src/RimMandrake/Webwork/Defs/ThingDefs_Buildings/RM_TractionLance.xml); frame inherits.
4. FIXED RM_LineCycleRoll: added priorityMode PrioritizeNearest (repo convention, 96 uses) in src/RimMandrake/RustCathedral/Defs/SoundDefs/RM_LineCycleSounds.xml.
5. REPORT ONLY: no textures for RM_SekkulaathSpleenChemicals, RM_SekkulaathCream (FEVERWOOD_BROOD_RANSOM_1 A2). No art generated.
Verified: all 3 files parse as XML. No live check.
