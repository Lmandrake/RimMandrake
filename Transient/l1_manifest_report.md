# L1 manifest report

Criteria: 62 across 59 items. Index: 7789 defNames from 2502 XML files; 0 parse failures (UNMEASURED).
Sanity probe: PASS (RM_Abyss present, fake name absent). get_defs call form: `defs` = single string "DefType/DefName" (one call per def).

Offline-present means the def exists in src/ XML; the live get_defs read is still owed (deploy state unproven offline).

- DEFS_NO_NAMES_FOUND: 10
- DEFS_UNRESOLVED_OFFLINE: 1
- NEEDS_LIVE: 17
- OFFLINE_PRESENT: 19
- OFFLINE_PRESENT_PROSE_DERIVED: 15

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
- SCALD_WATER_AGITATION_FLECKS_1 A1 defs=6 — The Scald terrains, agitation tags and setting defs resolve live via jawa/get_defs.
- VAULT_THAW_QUEST_FAMILY_1 A1 defs=9 — The eight vault quest defs resolve live via jawa/get_defs.
- GREENTIDE_BASE_PORT_BUILD_1 A2 defs=27 — jawa/get_defs on the free tier returns foundCount equal to 17 for the listed Greentide def
- WASTELAND_MECHANICS_BUILD_1 A1 defs=3 — The Wasteland defs resolve via jawa/get_defs with none in notFound.
- SCARLANDS_MECHANICS_2 A1 defs=18 — jawa/get_defs on the minimal list resolves the Scarlands mark, scaria incubation hediffs a
- STILLSAND_PRECIOUS_CAVES_LIVE_1 A1 defs=1 — The Stillsand mod deploys and its defs and genstep resolve on the minimal list.
- WARSCAR_RAINBOW_POOLS_1 A1 defs=8 — jawa/get_defs on the minimal list resolves the reagent defs and the liquid registry row.
- WYYYSCHOKK_FANG_PENDANT_1 A1 defs=2 — jawa/get_defs on the minimal list resolves the fang item, pendant apparel, recipes and tho
- WARSCAR_TOTCHAK_WAKES_1 A1 defs=1 — The totchak genstep, gnaw job and lie-down giver defs resolve live.
- RUST_CATHEDRAL_MECHANICS_1 A1 defs=4 — jawa/get_defs resolves all RustCathedral defs as expected.
- FOOTPRINT_TRACK_GRID_1 A2 defs=4 — The Stillsand track patch resolves live on the minimal list.
- SEA_FISHABLES_ALIVE_IN_DEPTHS_1 A2 defs=24 — Each sea's defs and wildAnimals resolve live on the minimal list with a living body for ev
- LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 A1 defs=2 — the Vissler arm resolves live as rottable and ingestible via jawa/get_defs
- SHIELD_MODS_LEVERAGE_1 A1 defs=2 — the four shield fields, landing advisory and hazard exposure tracker defs resolve live via
- SUMP_TAR_NASTINESS_1 A1 defs=16 — the tar kit defs resolve live under their RM_ names via jawa/get_defs

## DEFS_UNRESOLVED_OFFLINE
- UTINNI_WORLDMAP_FLIGHT_ICON_1 A1 MISSING=['RUT_Utinni'] — The UtinniWorldIcon texPath fields resolve live to the RUT_Utinni textures.

## DEFS_NO_NAMES_FOUND
- PYRINTH_FIRST_SCRIPT_1 A2 — the resolved-live checks in the Pyrinth script pass against jawa/get_defs on the minimal l
- SURFACE_RIVER_WEIRS_1 A1 — The River Works defs (weir, levee, silt trap, ferry, drift) resolve live after deploy.
- CAULDRON_ENRICHMENT_VISUALS_1 A1 — jawa/get_defs resolves the dewfall bead, flora accent, assay fleck and vexxiss print defs 
- LIQUID_INDUSTRY_SETPIECES_1 A1 — jawa/get_defs resolves the desal, detox, tar and pumping Wrecked, Kludged and Repaired def
- WRECKED_DISTILLATION_MODULE_1 A1 — the three distillation tier defs resolve live on the minimal list
- FORGE_WHITE_PLUME_FRONTS_1 A2 — The plume-front defs and settings resolve live on the minimal list via jawa/get_defs.
- FLOWWORKS_VISUAL_PRINCIPLES_1 A1 — jawa/get_defs resolves the surfaceLook data on the liquid defs as expected.
- FORCE_DISTURBANCE_REFLAVOR_1 A1 — after deploy, the patched psychic event defs resolve live with Force-flavoured label and l
- GRAVSHIP_ACOUSTIC_SCANNER_1 A1 — the Sounder, its research and the BiomeDef payload extension resolve live via jawa/get_def
- THE_SUMP_FIRST_SCRIPT_1 A2 — the 35 DEPLOY_HOLD held defs are resolved so their bars are measured rather than UNMEASURE

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
