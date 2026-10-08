# Live biomes sweep 2026-10-07 (FOUNDRY helper) - list acc_biomes-15

List: ModsConfig.xml parsed with ElementTree: 15 active (harmony, Core+5 DLC, rimbridgeserver, VFE Core, SimpleCameraSetting, AlphaBiomes, flowworks, gimmesomeslack, luminouspigment, mandrake.rm.biomes). Zero `mandrake.rut.*` and zero `mandrake.rsw.*`: this IS the free-tier list. jawa/running_mods agrees (15).
Method: jawa/get_defs, get_def, biome_probe, type_probe, mod_settings_field, harmony_patches, static_call over python.exe; Player.log copy Transient/bs_Player.log (312 lines, this 15-mod load; harvest_log run with --stale-ok because its def dump is from the previous run). Quicktest map started once (launch gate bypassed; cause below). Evidence files: Transient/bs_out1.json, bs_out2.json, bs_out3.json, bs_out5.json, bs_harvest.txt, l2sweep_<Mod>.json.

## Part 1: L1 criteria

| ID / criterion | verdict | evidence |
|---|---|---|
| GREENTIDE_BASE_PORT_BUILD_1 A2 | PASS | 17/17 listed RM_ defs foundCount=1 each, notFound empty (bs_out1.json); the four RUT_ originals notFound (moved, not aliased); ModsConfig has no mandrake.rut.* |
| STILLSAND_FIXES_LIVE_PROOF_1 A1 | PASS (caveat) | 0 log lines for TreeCategory "Standard", StartingHediff field, trainability = null, Megascarab meat, FrontLegs, BodyDef Rat; RM_KneelOllim found. Caveat: literal "No textures found at path Things/Plant/RM_" matches 15 lines, but none name a Contagion plant (they are Wasteland x6, Miasma Braskeen/Ismerrow, Greatbole/Kaddrath/Brakkel/Maddrick/Illurin tree folders); and this is the 15-mod list, not the full list |
| STILLSAND_FIXES_LIVE_PROOF_1 A2 | PASS | jawa/spawn_pawn RM_Oorrik faction none: spawned 1/1, kindActual RM_Oorrik, 0 "Error while generating pawn" lines |
| WARSCAR_SHEET_DONOR_PORT_1 A2 | PASS | ThingDef+PawnKindDef found for RM_Bileworm "bileworm", RM_JuggernautBeetle "juggernaut beetle", RM_ElectricGryllotalpa "electric gryllotalpa", RM_ElectricTick "electric tick", RM_Rimclaw "rimclaw"; biome_probe shows all five spawning in RM_Warscar (0.08/0.05/0.15/0.3/0.1) |
| RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A4 | PARTIAL (swbestiary-loaded half UNMEASURED) | no-swbestiary half PASS: biome_probe RM_RustCathedral animals = RM_CathedralRoach, RM_LivingBolt only; RSW_Mynock "absent, declared false"; PawnKindDef/RSW_Mynock notFound; 0 "Mynock" lines in log. The half that needs mandrake.rsw.swbestiary loaded cannot be measured here |
| GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1 A1 | PASS | RM_GreatboleSeed carries CompPlantable (plantDefToSpawn RM_Greatbole); RM_Greatbole thingClass RM_Plant_Greatbole (the water rule), type resolves from the on-disk DLL (mvid match); RM_GreentideSettings.greatboleServantsEnabled=False, greatboleSeedPlantingEnabled=True. Note: CompProperties_TreeConnection is only patched onto RM_GreatboleCore when the servants setting is on, so absent now by design |
| FORGE_DHOKKUR_WAYS_1 A1 | PASS | RM_Dhokkur has CompProperties_DhokkurWays (RM_CompDhokkurWays); RM_MapComponent_DhokkurPaths type resolves; TerrainDef RM_DhokkurPolishedTrail found; RM_TheForgeSettings carries all 8 dhokkur fields (wakeEffects, pathMemory, passesToPolish, trailsFade, trailFadeDays, wallShove, shoveMode, shoveDamagePct); 0 Dhokkur log lines |
| WARSCAR_CHOTRIX_SIGNS_1 A1 | UNMEASURED (criterion names a def that does not exist) | no def named RM_ChotrixPrint exists: prints are a raceOverride on RM_TrackSurfaceExtension carried by RM_Filth_SettledFilm (found; modExtensions [RM_TrackSurfaceExtension]); the raceOverride texPath is not readable by get_defs. JobDef RM_ChotrixDragKill, ThinkTreeDef RM_Chotrix found, JobDriver_ChotrixDragKill and RM_ChotrixTrackLink resolve; 0 Chotrix log lines. Criterion wording should name RM_Filth_SettledFilm |
| WARSCAR_AEROSOL_SCREEN_1 A1 | FAIL (suspected) | RM_AerosolScreen has RM_CompAerosolScreen; RM_PollutionSense and the comp resolve. harmony_patches: GameCondition_ToxicFallout.DoCellSteadyEffects has the RM_AerosolScreenPatches_FalloutCell prefix registered TWICE (owners mandrake.rm.warscar.totchak and mandrake.rm.warscar.chotrix), and NoxiousHazeUtility shows NO patched method at all (RM_AerosolScreenPatches_NoxiousHaze is not live; type-name resolution of the query not independently proven) |
| RUSTCATHEDRAL_GOODWILL_FLOOR_1 A1 | PASS | RM_BiomeAttitudeDef/RM_RustCathedralAttitude found: targetBiome RM_RustCathedral, standingStart 0, worstBandGoodwill* fields; RM_MapComponent_BiomeAttitude type resolves; static GetStanding(current map) returns null (map is not Cathedral, expected) |
| WEEPINGSTONES_CONDENSER_QUESTS_1 C6 (free-mod half) | PASS for free half; campaign half UNMEASURED | slots read live: Buyer preferredFactions [Empire] fallback Collector, Settlers [OutlanderCivil], Hunters [Pirate]; FactionDef/RUT_Jawa_HuttCartel notFound on this list; both QuestScriptDefs found. Free-mod text search for Hutt/Blackstar not run in this pass; campaign half needs the Utinni list. Not recorded |
| GREENTIDE A2/free-tier consistency | FINDING | RM_FloodedCanyon BiomeDef (free tier) names RUT_EmperorVulture, RUT_SealedSleeper, RSW_SandLeaper, RSW_SandPillar, RSW_Creature_Mantrap, RSW_MutagenicNorphea: 6 unresolved cross-references on a list without those mods, plus a BiomeDef.ConfigErrors NullReferenceException for RM_FloodedCanyon |

### Player.log: config errors naming our defs (this load)
- RM_Thurrock discarded: type RimMandrake.EnvironmentalHazards.HediffCompProperties_PeriodicAreaAttackSecondary not found. Source file exists (`src/RimMandrake/EnvironmentalHazards/Source/HediffComp_PeriodicAreaAttackSecondary.cs`) but jawa/type_probe says the deployed EnvironmentalHazards DLL does not carry it: stale DLL, needs winbuild + redeploy. Cascades: RM_ThurrockShatter unresolved (Greentide chain FAIL below).
- RM_FE_Ash_Trace, Ash_Light, Ground_Sand, Gravel, Soil, SoilRich: "burnedDef is flammable" (x2 each)
- RM_LineCycleRoll: PrioritizeNewest is not supported with sustainers
- RM_TractionLance and Frame_RM_TractionLance: madeFromStuff but has a defined constructEffect
- RM_LongShadeWreckSpeeder: graphicData defines a shadowInfo but staticSunShadowHeight > 0
- Exception in ConfigErrors() of RM_FloodedCanyon (NRE in BiomeDef.ConfigErrors)
- Eclipse/SolarFlare/Aurora: world-targeting incident has a biome restriction list
- 10 unresolved cross-references (6 FloodedCanyon roster rows above, Leather_Chitin x3 for RM_ races in LongShade/Pyrelands/Abyss, RM_ThurrockShatter), 15 "No textures found" Collection-init lines, RM_Tuun/RM_LungerFry missing vanilla plant textures, TheSump Patch FindMod failure RUT_SumpDuskLock_BiomeWiring (expected, no campaign layer)
- RM_WM_* smelter/distillation errors are absent: WreckedMachines is not on this list.

## Part 2: L2 / GREEN-MIN chains (Session on the running quicktest map)
Map: one quicktest map started via runner.ensure_playing_map with the launch gate bypassed; the only blocker is the same RM_Thurrock hediff comp type from EnvironmentalHazards. Game left running and paused on the map. Suites killed by my own per-mod timeout (no JSON written): Stillsand, Cauldron, FeverWood, NightsideIce, TheForge, Wasteland (bridge timed out mid-run), WeepingStones (500 s); full suites for those need more than 3 to 8 minutes each and were not completed. Contagion, MovingDunes, Webwork, Pyrelands, Abyss, BlueDesert, LeaningScrub, TheRot, Miasma, TerminalBiomes, GelatinousSlime, GimmeSomeSlack, LuminousPigment, FlowWorks: not run (45 min budget).

| mod suite | result | notes |
|---|---|---|
| TheSump | 29 PASS / 0 FAIL / 11 UNMEASURED | UNMEASURED are map-generation-only rows (needs a map GENERATED as RM_TheSump; 0 tiles until the repaint) and kethrel home-area. THE_SUMP_FIRST_SCRIPT_1 A3/A4 not closed: A3 asks for a northstar_driver run, this was a validation.py chain run |
| Greentide | 52 PASS / 2 FAIL / 10 UNMEASURED | FAIL shipped_defs_resolve: HediffDef/RM_ThurrockShatter notFound (cause: stale EnvironmentalHazards DLL, above; mod/deploy defect). FAIL swallow_buries_on_churnmud_only: steel left 3200 ticks on RM_GreentideChurnmud not swallowed (unclassified: either RM_MapComponent_MudSwallow dead on a non-Greentide map or a harness precondition; downstream 2 UNMEASURED). 10 UNMEASURED need worldgen |
| RustCathedral | 47 PASS / 1 FAIL / 21 UNMEASURED | FAIL RM_Setti_crossBiomeBiomeList_round_trips: "get returned no value" for a null string setting (harness: a null string has no value to read back; classification harness, not mod); 10 downstream round-trips UNMEASURED upstream-failed. 11 map-mechanic rows UNMEASURED (needs a generated RM_RustCathedral map) |
| LanternDeeps | 33 PASS / 0 FAIL / 4 UNMEASURED | UNMEASURED need a Lantern Deep pocket map |
| FloodedCanyon | 43 PASS / 0 FAIL / 10 UNMEASURED | UNMEASURED: Explosive Growth not loaded, ledge spawn site, no tool for several rows. Note: the chain passed although the BiomeDef raises ConfigErrors NRE |

No L2 criterion in the acceptance list maps one-to-one onto these suite verdicts, so no L2 pass was recorded.

## Recorded with rimflow verify (config acc_biomes-15)
GREENTIDE_BASE_PORT_BUILD_1 A2; STILLSAND_FIXES_LIVE_PROOF_1 A1, A2; WARSCAR_SHEET_DONOR_PORT_1 A2; GREATBOLE_ATMOSPHERE_AND_CROSSOVERS_1 A1; FORGE_DHOKKUR_WAYS_1 A1; RUSTCATHEDRAL_GOODWILL_FLOOR_1 A1 (all L1 pass); RUSTCATHEDRAL_BASE_FINISH_BUILD_1 A4 recorded as partial.
