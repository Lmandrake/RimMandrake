# acc_biomes fixes 2026-10-08 (source work only, no live game)

Verdicts: REAL = mod bug fixed; HARNESS = validation.py defect fixed; OPEN = not resolvable offline.

- GELATINOUSSLIME_SEEKER_MARK_FAILS_1: REAL + HARNESS. RM_Gene_B25_TheReek / A16_PheromoneCharm live in the Utinni layer,
  absent from the 15-mod tier, so SlimeDefs.TheReek is null and `comp.RiderGene == SlimeDefs.TheReek` was true for a
  rider-less seeker (null == null): mark doubled. Fixed with a null guard (GeneSeeker.cs:541); validation now UNMEASURED
  when the genes are not loaded. Regression: selftest_slime_suite.py source check. DLL rebuilt.
- STILLSAND_SANDSWIM_GRAVEL_SUBMERGE_1: HARNESS. IsSwimTerrain reads only Sand/SoftSand/RM_DeepSand. The 10x6 gravel patch let
  the vekka wander onto sand in 300 ticks. Patch is now 24x12. Selftest 106/106.
- STILLSAND_LOOMMA_SUNSTRUCK_SHADE_1: HARNESS. ShadeAt uses the roof layer correctly; loommas forage the shade rim and
  leave the roof patch. Pawns now count only if on their side at both samples (300/600). Selftest 106/106.
- LEANINGSCRUB_BLOOM_TOGGLE_OFF_STILL_FIRES_1: HARNESS. MapComponentTick returns at line 1 when off; vanilla animals flee an
  approaching colonist with no bloom. OFF arm now fails on vissler arms (bloom-only) not Flee. Selftest 68/68.
- AEROSOL_SCREEN_STATICCTOR_WARN_1: REAL. Static Material moved into a nested [StaticConstructorOnStartup] holder
  (RM_AerosolScreen.cs). DLL rebuilt. No offline test possible (engine load warning); verify on next load.
- RUSTCATHEDRAL_SETTINGS_CROSSBIOME_ROUNDTRIP_1: HARNESS. crossBiomeBiomeList defaults to "" and the bridge reads an empty
  string as null (suite.py documents the same). A None string now starts as "" and the set/read-back still proves the field.
- WASTELAND_TOXIC_BUILDUP_NEVER_APPLIES_1 (+ WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1 dose rows): HARNESS. ToxicUtility.CheckInterval
  is 3451 ticks (RimSage) and both the storm layer and RM_CompAmbientDose dose only on it; every dose check waited 420-900.
  Added _wait_dose (>= 3571 ticks); mock heat slowed so the heat-off test still discriminates. Selftest passes.
  OPEN: tippingEnabled=false still yields a quest via fire_quest, middenshellEnabled=false dry-run canFireNow=True. Source
  gates are present (TestRunInt, CanFireNowSub); fire_quest probably bypasses TestRun, cause of the incident row unknown
  without live. Gripper/brine 30s timeouts: frame-bound bridge, not source. Processor 'off feed ground', Pusberry/Boilbulb
  harvest: not examined (no source cause found; needs live).
- MIASMA_MOTHERS_PRICE_RETURN_SITE_1: HARNESS. 'ERROR no warden mother and no water cell' now records UNMEASURED.
- CONTAGION_LIVE_SUITE_FAILS_ACC_BIOMES_1: HARNESS/OPEN. native_dives_for_roof is site placement; inject 30s timeout is
  frame-bound; coalescence 'no manhunter after 7000 ticks' not resolvable offline.
- LINKED_GRAPHIC_ICON_NRE_1: OPEN, not ours as far as source shows. All 9 of our Linked/CornerFiller graphicDatas resolve
  (checked in source and deployed Mods). Candidate: DV_PyrinthLamp uses Graphic_Random on a single PNG
  ('Collection cannot init ... Things/Building/Misc/PyrinthLamp', Pyrinth Absorbed_EpochsPyrinth_Buildings_Furniture.xml:88),
  and GimmeSomeSlack (donor) rewrites conduit graphics. Needs live to name the def.
- Not examined: CAULDRON_YIELD_HARVEST_ORDER_FAIL_1, SCARLANDS_CHATRAK_SNAP_STAGE_02_1, CREATUREBEHAVIORS_TRACKGRID_BRIDGE_TIMEOUT_1,
  WRECKAGE_SCALD_FIELD_MISCLASSIFIED_1 (outside the brief).
