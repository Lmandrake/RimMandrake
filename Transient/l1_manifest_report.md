# L1 manifest report

Criteria: 62 across 59 items. Index: 7813 defNames from 2511 XML files; 0 parse failures (UNMEASURED).
Sanity probe: PASS (RM_Abyss present, fake name absent). get_defs call form: `defs` = single string "DefType/DefName" (one call per def).

Offline-present means the def exists in src/ XML; the live get_defs read is still owed (deploy state unproven offline).

- NEEDS_LIVE: 17
- NO_DEFS_AUTHORED: 1
- OFFLINE_PRESENT: 19
- OVERRIDE_VERIFIED: 22
- OVERRIDE_VERIFIED_PLUS_EXTERNAL: 3

## OVERRIDE_VERIFIED
- SCALD_WATER_AGITATION_FLECKS_1 A1 defs=7 — The Scald terrains, agitation tags and setting defs resolve live via jawa/get_defs.
  - note: Agitation 'tags' (RM_WaterAgitationLight / RM_WaterAgitationHeavy) are terrainTags on the terrains, and the 'setting defs' are Mod Settings fields; neither is a def. Check the tags with a terrain field read, not get_defs presence. The three wreck defs (RUT_ScaldWreck*) belong to the shadow fix, not this criterion's wording.
- VAULT_THAW_QUEST_FAMILY_1 A1 defs=8 — The eight vault quest defs resolve live via jawa/get_defs.
  - note: Exactly the eight QuestScriptDefs, in src/RimUtinni/StructureInjectionsRUT/Defs/VaultDungeons/QuestScriptDefs/RUT_VaultThaw.xml (the item prose says src/RimUtinni/VaultDungeons/, which is stale).
- GREENTIDE_BASE_PORT_BUILD_1 A2 defs=17 — jawa/get_defs on the free tier returns foundCount equal to 17 for the listed Greentide def
  - note: The 17 typed names are copied from the item's own ## criteria list (foundCount must equal 17).
- PYRINTH_FIRST_SCRIPT_1 A2 defs=13 — the resolved-live checks in the Pyrinth script pass against jawa/get_defs on the minimal l
  - note: The script's defs_resolve bar reads every def parsed from the mod's own XML; this is that set. validation.py itself says a live read cannot tell this dormant pack from the donor det.epochspyrinth.
- SURFACE_RIVER_WEIRS_1 A1 defs=10 — The River Works defs (weir, levee, silt trap, ferry, drift) resolve live after deploy.
  - note: River Works was merged into FlowWorks (409d1f57c): the defs live in src/RimMandrake/FlowWorks/Defs/Rivers/, and the old src/RimMandrake/RiverWorks folder is gone. The LEVEE is the continuous RM_BankStake line (RM_BankWorks.xml: 'a continuous line of them holds back a flood like a levee'); no def is named levee. Drift is five RM_RiverDriftDef rows whose DefType is a namespaced class, so confirm get_defs accepts that spelling.
- WASTELAND_MECHANICS_BUILD_1 A1 defs=14 — The Wasteland defs resolve via jawa/get_defs with none in notFound.
  - note: Built defs for the item's four mechanics. The Middenshell def exists but the ruled 20-cell width exceeds the engine's 4x4 footprint (FOUNDRY note 2026-09-30, owner call); RM_WastelandPlasmaStorm is 'def only, UNWIRED'. Presence is not function.
- CAULDRON_ENRICHMENT_VISUALS_1 A1 defs=4 — jawa/get_defs resolves the dewfall bead, flora accent, assay fleck and vexxiss print defs 
  - note: Only the bead is a standalone def. Assay flecks = RM_AssayFlecksExtension on RM_TwistingThornwood and RM_TreeMartyr (modExtension, overlay art owed so dormant). Vexxiss prints = code (RM_VexxissPrints.cs) hung off RM_CompVexxissBehaviour on RM_Vexxiss, no print def. Flora-accent dew variant: NO def and NO XML extension exists in src/ (RM_DewfallGraphicExtension is C# only, 'DORMANT, no XML ext added' per Transient/cauldron_visuals_20261006.md), so that quarter of the criterion has nothing to resolve. See BUILD DEFECTS.
- LIQUID_INDUSTRY_SETPIECES_1 A1 defs=12 — jawa/get_defs resolves the desal, detox, tar and pumping Wrecked, Kludged and Repaired def
  - note: Twelve tier defs (4 machines x Wrecked/Kludged/Repaired). Each machine also has a *_RuinScatter def, not asked for here.
- WRECKED_DISTILLATION_MODULE_1 A1 defs=3 — the three distillation tier defs resolve live on the minimal list
  - note: These three exist ONLY as PatchOperationAdd values in WreckedMachines/Patches/WreckedMachines_DistillationModule.xml, guarded by PatchOperationFindMod 'RimMandrake: FlowWorks'. They resolve live only when FlowWorks is in the list.
- SCARLANDS_MECHANICS_2 A1 defs=6 — jawa/get_defs on the minimal list resolves the Scarlands mark, scaria incubation hediffs a
  - note: The criterion text is cut in the queue view ('... sentinel defs wit...'). No Sentinel PawnKindDef exists in src/; RUT_SentinelGraveWard (a ThingDef) is the only sentinel body. If the full criterion wants a sentinel kind, that is absent.
- STILLSAND_PRECIOUS_CAVES_LIVE_1 A1 defs=8 — The Stillsand mod deploys and its defs and genstep resolve on the minimal list.
  - note: Two genstep defs plus the five RM_PreciousCaveDef rows; the biome carries the genstep via extraGenSteps (patch RM_PreciousCaves_BiomeGenSteps.xml). Four more cave rows live in the RSW_/RUT_ tiers and are not asked for on the minimal list.
- WARSCAR_RAINBOW_POOLS_1 A1 defs=5 — jawa/get_defs on the minimal list resolves the reagent defs and the liquid registry row.
  - note: Four reagent items plus the registry row. RM_ReactionPool/RM_ReactionTap/RM_ReactionPools genstep exist too but are not 'reagent defs'. The earlier prose-derived list wrongly included RM_GlowerCrust.
- WYYYSCHOKK_FANG_PENDANT_1 A1 defs=4 — jawa/get_defs on the minimal list resolves the fang item, pendant apparel, recipes and tho
  - note: One recipe exists (criterion says 'recipes'). The thought's workerClass RSW_ThoughtWorker_ObserverFactionApparel is C#, so the worker resolving is a ThoughtDef load, not a def lookup.
- WARSCAR_TOTCHAK_WAKES_1 A1 defs=4 — The totchak genstep, gnaw job and lie-down giver defs resolve live.
  - note: CORRECTED: the prose-derived name RUT_SealedSleeper was the wrong creature (the sealed sleeper, not the totchak). The lie-down 'giver' is a JobGiver C# class reached via the think tree (ThinkTreeDef RM_Totchak, file RM_ThinkTree_Totchak.xml); the def is JobDef RM_TotchakLieDown.
- FLOWWORKS_VISUAL_PRINCIPLES_1 A1 defs=20 — jawa/get_defs resolves the surfaceLook data on the liquid defs as expected.
  - note: Fifteen LiquidDefs carry surfaceLook inline; FluidDefs (oil, poison, blood, chemfuel, astrofuel) get it by patch. DefType spellings are namespaced classes; confirm what get_defs accepts.
- RUST_CATHEDRAL_MECHANICS_1 A1 defs=33 — jawa/get_defs resolves all RustCathedral defs as expected.
  - note: CORRECTED: the shipping mod is src/RimMandrake/RustCathedral (RM_ tier); the prose-derived RUT_CathedralRoach/RUT_ScarRoach/RUT_RustCathedral are the RimUtinni twins and not what 'all RustCathedral defs' means. The twin roaches live in src/RimUtinni/RustCathedralRoaches.
- SEA_FISHABLES_ALIVE_IN_DEPTHS_1 A2 defs=100 — Each sea's defs and wildAnimals resolve live on the minimal list with a living body for ev
  - note: Derived from the four sea BiomeDefs (RM_GreySea, RM_TwilightSea, RM_TheScald, RM_TheChill): every fishTypes catch plus its living body from wildAnimals (inline or patch-added). A catch with no living body is a build defect.
- GRAVSHIP_ACOUSTIC_SCANNER_1 A1 defs=5 — the Sounder, its research and the BiomeDef payload extension resolve live via jawa/get_def
  - note: The payload extension is patched onto exactly three BiomeDefs (FloodedCanyon, Stillsand, CrackedLands). The item says 'a per-biome payload in EVERY biome'; only three biomes carry one. That gap is a build fact for A2/A3, see BUILD DEFECTS.
- LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A1 defs=1 — the Vissler arm resolves live as rottable and ingestible via jawa/get_defs
  - note: Only the arm item is asked for. 'rottable and ingestible' is a field read on the def, not presence.
- SHIELD_MODS_LEVERAGE_1 A1 defs=5 — the four shield fields, landing advisory and hazard exposure tracker defs resolve live via
  - note: The 'four shield fields' are ShieldFieldMode enum values, and the landing advisory / hazard exposure tracker are C# classes (ShieldLandingAdvisory.cs, ShieldHazardExposureTracker.cs): none is a def, so get_defs cannot show them. They need a state read.
- SUMP_TAR_NASTINESS_1 A1 defs=9 — the tar kit defs resolve live under their RM_ names via jawa/get_defs
  - note: Nine tar-kit defs under RM_ names. The prose-derived RSW_RemoveBrainWorm / RUT_Hardwood / RUT_Greenwood were noise.
- THE_SUMP_FIRST_SCRIPT_1 A2 defs=35 — the 35 DEPLOY_HOLD held defs are resolved so their bars are measured rather than UNMEASURE
  - note: STALE PREMISE: src/DEPLOY_HOLD.txt has no active TheSump line (the 11 holds were lifted 2026-10-03, comment at its line 443), so no def is 'held' now. These eight files are the former hold group (9+3+18+1+1+1+1+1 = 35 defs, the criterion's number). Re-word A2 as 'every TheSump def resolves'.

## OVERRIDE_VERIFIED_PLUS_EXTERNAL
- FOOTPRINT_TRACK_GRID_1 A2 defs=2 — The Stillsand track patch resolves live on the minimal list.
  - EXTERNAL: ['TerrainDef/Sand']
  - note: The patch adds RM_TrackSurfaceExtension to vanilla TerrainDef/Sand and to RM_DeepSand. Vanilla Sand is external (UNMEASURED offline).
- UTINNI_WORLDMAP_FLIGHT_ICON_1 A1 — The UtinniWorldIcon texPath fields resolve live to the RUT_Utinni textures.
  - EXTERNAL: ['WorldObjectDef/Gravship']
  - note: `RUT_Utinni` is a TEXTURE name (Textures/World/WorldObjects/Expanding/RUT_Utinni.png and World/WorldObjects/RUT_UtinniCaravan.png, both on disk), never a def. The only def is vanilla/Odyssey WorldObjectDef/Gravship, patched by src/RimUtinni/UtinniPatches/Patches/UtinniWorldIcon.xml. Live read must check expandingIconTexture and texture on Gravship. Commit df9370e09 already recorded that the deployed patch was NOT rendering live.
- FORCE_DISTURBANCE_REFLAVOR_1 A1 — after deploy, the patched psychic event defs resolve live with Force-flavoured label and l
  - EXTERNAL: ['GameConditionDef/PsychicDrone', 'GameConditionDef/PsychicDroner', 'GameConditionDef/PsychicRain', 'GameConditionDef/PsychicSoothe', 'GameConditionDef/PsychicSuppression', 'GameConditionDef/VEE_PsychicBloom', 'GameConditionDef/VEE_PsychicHum', 'GameConditionDef/VEE_PsychicOverdrive', 'GameConditionDef/VEE_PsychicStimulation', 'GameConditionDef/VREA_PsychicStorm', 'IncidentDef/PsychicDrone', 'IncidentDef/PsychicEmanatorShipPartCrash', 'IncidentDef/PsychicSoothe', 'IncidentDef/VEE_PsychicBloom', 'IncidentDef/VEE_PsychicHum', 'IncidentDef/VEE_PsychicOverdrive', 'IncidentDef/VEE_PsychicRain', 'IncidentDef/VEE_PsychicStimulation', 'IncidentDef/VREA_PsychicStorm']
  - note: Every target is a vanilla/DLC/donor def (PsychicDrone, PsychicSoothe, PsychicEmanatorShipPartCrash, PsychicDroner, PsychicSuppression and VEE_* donor rows), so none is in src/. They are UNMEASURED offline by construction; VEE_* only exist if that donor is loaded.

## OVERRIDE_DEFECT_OR_AMBIGUOUS

## NO_DEFS_AUTHORED
- FORGE_WHITE_PLUME_FRONTS_1 A2 — The plume-front defs and settings resolve live on the minimal list via jawa/get_defs.
  - note: The plume-front build (09ccb3ca5) is C# + Mod Settings only: RM_MapComponent_PlumeFronts, RM_ForgePlumeFronts.cs, six settings (plumeFrontsEnabled, plumeObscureEnabled, plumeSoakEnabled, plumeHeatEnabled, plumeAdaptedExempt, plumeStrength). It authors NO def; the only defs it touches are vanilla (Filth_Water, GasType.BlindSmoke is an enum). The criterion's 'plume-front defs' do not exist. Re-word A2 as a settings read (the six names above) before a live round.

## OFFLINE_PRESENT
- FALL_LINE_FERAL_SURVIVOR_PAWNKIND_1 A2 defs=2 — RUT_FeralSurvivor and RUT_Hediff_FeralScar resolve live on the minimal list via jawa/get_d
- MINDSTONE_MATRIX_KINDLED_BUILD_1 A1 defs=1 — The mindstone recipes, RSW_DW_Head_Mindstone and related defs resolve live on the minimal 
- BARBSLINGER_SCORPION_REDESIGN_1 A1 defs=2 — jawa/get_defs resolves RM_Barbslinger and RM_BarbslingerTailGun comps with no missing type
- FEVERWOOD_BOUGH_SOIL_TERRAIN_1 A1 defs=1 — jawa/get_defs returns RUT_BoughSoil with foundCount 1 and fertility as expected
- STILLSAND_GEOPHONE_1 A1 defs=1 — jawa/get_defs resolves RM_Geophone with expected fields
- DROIDWORKS_WIPE_SEVERITY_1 A1 defs=1 — jawa/get_defs on the minimal list resolves RSW_DW_RecentlyWiped and the five quirk traits 
- FEVERWOOD_RM_CAST_COMPLETION_1 A1 defs=1 — jawa/get_defs on the minimal list for the seven creature ThingDefs and PawnKindDefs plus R
- FORGE_SPUNSTONE_SOURCES_1 A1 defs=2 — jawa/get_defs on the minimal list resolves RM_FloatstoneDoor, RM_SpunstoneHull and the sal
- PIT_TEMPERATURE_SOFTENING_1 A1 defs=1 — jawa/get_defs on the minimal list resolves the exposure hediff and RM_ExposedPrisoner thou
- ARMOURY_KOTOR_BOLT_GUARD_1 A1 defs=1 — After deploying Armoury, jawa/get_defs shows KotORBlasterBolt_default ranged patch damage 
- STILLSAND_SAND_SIEVE_CHORE_1 A1 defs=2 — jawa/get_defs resolves RM_SandSieve, the RM_SiftGlassSand job and its WorkGiver.
- WEBWORK_TRACTION_LANCE_BUILD_1 A2 defs=1 — jawa/get_defs resolves RM_TractionLance, its research def and the repointed junctions.
- FIREHAWK_FLIGHT_BEHAVIOR_1 A2 defs=1 — jawa/get_defs resolves the flyingAnimation fields on the RM_FireHawk PawnKindDef as expect
- GREENTIDE_STELLOCK_LACE_BUILD_1 A1 defs=1 — jawa/get_defs resolves RM_StellockBranch, Lace and Laced defs as expected.
- STILLSAND_CAVE_AS_PLACE_1 A1 defs=2 — jawa/get_defs resolves the Stillsand cave preservation, RM_CaveDrip and RM_GrownBiosilicaW
- STILLSAND_SUN_LANCE_1 A1 defs=1 — jawa/get_defs resolves RM_SunLance as expected.
- WARSCAR_TURRETS_TRACK_1 A1 defs=1 — jawa/get_defs resolves RM_OldLineTurret and its patch as expected.
- GREENTIDE_THURROCK_HERD_BUILD_1 A2 defs=2 — RM_Thurrock race, kind, RM_ThurrockShatter and the aura applier defs resolve live on the m
- GELATINOUSSLIME_TITAN_CHUNK_BOMB_1 A1 defs=1 — jawa/get_defs ThingDef/RM_TitanoslimeChunk returns foundCount 1

## OFFLINE_PRESENT_PROSE_DERIVED

## DEFS_UNRESOLVED_OFFLINE

## DEFS_NO_NAMES_FOUND

## NEEDS_LIVE
- FORGE_ENRICHMENT_QUICKTEST_1 A5 defs=3 live=['log'] — Player.log is clean of the four named defs after load.
- JAWABENCH_DLL_STALE_REBUILD_1 A2 live=['tool list'] — The flowworks_pulse and static_call tools appear in the live tool list once the game is up
- MOD_OPTIONS_RETROFIT_1 A1 defs=4 live=['settings'] — On a full-list load Mod Settings opens for each of our mods with no red errors.
- STILLSAND_FIXES_LIVE_PROOF_1 A1 defs=5 live=['log'] — The full-list load log shows the expected strings for the Stillsand fixes.
- STILLSAND_FIXES_LIVE_PROOF_1 A2 defs=1 live=['state-read'] — spawn_pawn of RM_Oorrik succeeds.
- JAWA_SWIM_HOOD_KEEP_1 A1 live=['state-read'] — the deployed JawaRules DLL state-read shows Apparel_Head.CanDrawNow true for a swimming Ja
- MOVING_DUNES_BUILD_1 A3 defs=2 live=['state-read'] — the shader tint gate (MaterialColor vs VertexColor) is resolved by a live load
- LIVE_ROUND2_FIXES_PROOF_1 A3 defs=4 live=['log'] — Player.log after the WhisperSarlaccSign genstep shows 0 MakeThing stuff=null errors.
- DEBUG_ACTION_ENUM_CRASH_1 A1 live=['state-read'] — jawa/debug_action_yielders called live in the main-menu state returns without crashing.
- DEBUG_ACTION_ENUM_CRASH_1 A2 live=['state-read'] — jawa/debug_action_yielders called live in a loaded-game state returns without crashing.
- GRAFFITI_NORTHSTAR_BRIDGE_TOOLS_1 A1 live=['tool list'] — thing_graphic, spawn_variant, running_mods, glow_at and site_state appear in the live tool
- LASSO_CHERRYPICKER_REMOVAL_1 A1 live=['state-read'] — The live CherryPicker config is reconciled (2133 unrecognised cuts) and cherrypicker_swap 
- LASSO_CHERRYPICKER_REMOVAL_1 A2 live=['settings'] — Melee Animation LassoSpawnChance is set to 0.
- ARMOURY_PROJECTILE_DAMAGE_TOOL_1 A3 live=['state-read'] — jawa/projectile_damage returns the vanilla control value (Bullet_Revolver 12) live on the 
- LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 A1 defs=1 live=['state-read'] — The flora_spawns check passes after fixing the RM_Grellspine failure.
- PROXIMITY_HATCH_FIRST_SCRIPT_1 A2 live=['state-read'] — The settings and defs_resolve checks pass live on the minimal list.
- NORTHSTAR_COMPANION_GAPS_1 A1 — the six JawaBenchSituationalTools tools (pawn_census, pawn_roles, incident_queue_peek, inc

## BUILD DEFECTS AND CRITERION MISMATCHES (from overrides; real findings, not papered over)
- CAULDRON_ENRICHMENT_VISUALS_1 A1: A1 asks for the flora-accent dew defs; src/ holds no def or XML modExtension for dewfall saturation (RM_DewfallGraphicExtension is C#-only, dormant pending dew art and the owner's accent-plant pick). Only 3 of the 4 named things have a def anchor. Build gap for the saturation half, not a typo.
- FORGE_WHITE_PLUME_FRONTS_1 A2: A2 names 'the plume-front defs'; the build authored none (code plus six settings only). Criterion/build mismatch: either re-word A2 to a settings read or build the defs the criterion expects.
- UTINNI_WORLDMAP_FLIGHT_ICON_1 A1: The one criterion naming a name absent from src/ (RUT_Utinni) was a texture folder, not a def, so no def is missing. Real defect on record: commit df9370e09 found the deployed icon patch is NOT rendering live.
- GRAVSHIP_ACOUSTIC_SCANNER_1 A1: Item says a payload in EVERY biome; src/ has the RM_AcousticPayloadExtension patched onto only 3 BiomeDefs (RM_FloodedCanyon, RM_Stillsand, RUT_CrackedLands). A1 resolves; the every-biome claim is unbuilt.
- THE_SUMP_FIRST_SCRIPT_1 A2: A2's premise ('35 DEPLOY_HOLD held defs') is stale: all TheSump holds were lifted 2026-10-03, so 0 defs are held now. Not a missing def; the criterion needs re-wording.
- Rows whose named def is absent from src/ after override resolution: 0
