# LOAD13_CONFIGERRORS_TRIAGE_1

Load 13 (2026-10-03 22:08, 637 mods) harvest, `Transient/belt_harvest10_20261003.txt`. Our own def ConfigErrors still standing
(engine source read through RimSage, not assumed):

- `RM_TarShallow` "makes terrain filth and also accepts it" — TerrainDef.ConfigErrors (Verse/TerrainDef.cs:538) rejects
  `generatedFilth != null && (filthAcceptanceMask & Terrain) != 0`. `RUT_TarShallow_FilthAcceptance.xml` sets mask `[Terrain]`
  (so `RUT_Filth_MouseTrack`, placementMask `[Terrain]`, passes FilthMaker.TerrainAcceptsFilth) and
  `RUT_TarShallow_GeneratedFilth.xml` sets `generatedFilth RM_Filth_Tar`. The two patches contradict the engine's own rule; the
  patch headers read TerrainDef.cs:538 backwards. NEXT: decide the shape (mouse-track filth placementMask `[Pawn]` + tar mask
  `[Natural,Unnatural,Pawn]`, or drop generatedFilth) then rerun TheSump walkways + mouse-track chains.
- `RUT_ComplexStructures`, `RUT_Slough_GelatinousBreach`: LandmarkDef "has no mutators with a chance of 1 or higher".
- `RUT_Reckoning_CartelOffer`: non-root quest has defaultChallengeRating.
- `RSW_DeepDesertSeep`: building category + deconstructible but thingClass `Thing` (Sarlacc/ThingDefs_SarlaccSeep.xml).
- `RUT_Tree_Hearth` research view collisions with ModernFixtures / VCE_StewCooking (same coords+tab, both donor defs).
- `CannibalPirate`, `PirateYttakin`: NullReferenceException in ConfigErrors().
- By design, leave: `RM_FE_Ash_*/Ground_*` "burnedDef is flammable" (ScorchableGround.xml header says so).
- FIXED this pass: `RM_VisslerArm`, `RM_QeshraRoe` (`socialPropernessMatters` is a ThingDef field; it sat inside `<ingestible>`).
