# LIVE_NEEDS_ENFORCE_ABSENCE_NOW_EXPLICIT: evidence (2026-11-06)

What the pre-slot gate now adds to a proof's planned load (`relentless_names.needs`, called from
`relentless_live_round.mod_gap` / `batch_gap` and the run row), measured three ways. Nothing here is written into
any proof: the gate derives it every time. Design of record: `design/RimMandrake/live_mods_filing_check_2026-11-05.md` §5/§7,
changed by the item (enforce, derive at the gate, `live-without:`).

## 1 Historical replay (criteria 1 and 2)

`python3 src/RimMandrake/rimflow/relentless_names.py replay --enforce --fixture src/RimMandrake/rimflow/fixtures/live_mods_replay.json`

- R1/R2 items right: **17 of 20** (bar 17). An item is right only when EVERY one of its frozen failed runs would have had
  each mod its next repair added in the planned load.
- Wrong additions: **0**, across the 57 failed runs and the 50 last PASS proofs. An addition outside the repair's own
  names counts as right only when its evidence states the need (`SELF_EVIDENT` in relentless_names.py: a hard About.xml
  dependency, the composed mod of the build's folded source, the proof's own `--needs`/`--enable`/staging line, the mod
  the proof script lives in, a fixture save's modIds).
- PASS proofs: **46 additions on 50**, none wrong. Criterion 2 as written ("zero additions on the last 50 PASS proofs")
  cannot hold and is the wrong bar: those proofs passed on loads that happened to hold mods their own text names
  (`--needs ebsg.framework`, "Stager: the list ALSO needs ..."), or that a mod they load hard-depends on. Adding a mod a
  PASS proof already had loaded changes nothing; the measurable defect is a WRONG addition, and there are none.
- Misses (3): ART_OVERRIDE_FAMILY_SCRIPT_1 (sarg.alphamemes, VE genetics named only as quoted packageIds in a JSON
  manifest beside four retired donors the repair did not add), TITANIC_BODYSIZE_TEST_RACE_1 (its first run names Large
  Pawns only in a script docstring), WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR (MenuShell only on a prose line of a
  helper). Each stays a warning: promoting those sources adds wrong mods elsewhere in the replay.

The defName source (`--has XDef/RM_...`, single owner from the repo's Defs) is tested offline but is not in the frozen
replay index (the fixture predates it); the migration below shows its live additions. A stale index (a mod whose deployed
DLL's `.srchash` is not the repo's) degrades type and defName needs to warnings; file mtimes were tried first and read
EVERY mod stale in a fresh clone.

## 2 Migration over every live proof (spec step 5)

`python3 src/RimMandrake/rimflow/relentless_names.py migrate` over `infrastructure/state/live_proofs/*.txt` (proof text
alone, no build mods, so a build's own mod shows here as an addition the gate would not need; real index of this
machine, 2026-11-06): **163 proofs, 84 with additions, 150 additions, 0 conflicts.** Every addition was cross-checked
against the proof's own `--without`/`--absent` arguments. One contradicted the proof's intent:
STILLSAND_RETURN_REMAINDER_1 clause A2 runs `--without mandrake.rut.patches` (the RM tier with Utinni absent) while
A1/A4 `--needs` it; it now carries `live-without: mandrake.rut.patches`. Two others only looked like it:
MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG (`--absent MineShaft`) and VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT (`--absent
SolarMirrors`) pass those names to live_log_check.py, a log-string absence check, beside `--has` asserts that need the
mod loaded: no change.

| proof | additions (mod, source) |
|---|---|
| ART_RESOLUTION_MEASURE_AT_MAX_ZOOM | UtinniPatches (script_path), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP | AtmosphericBase (script_home), UtinniPatches (script_path), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| BIG_REPAINT_FINISH_ONCE_AND_FOR_ALL | UtinniPatches (script_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| BIOME_TIER_CLEANUP_1 | UtinniPatches (proof_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| BLUEDESERT_FLORA_PLANT_REFUSAL_1 | RimMandrake.Biomes (script_home) |
| BLUEDESERT_GPT_ENRICHMENT_1 | RimMandrake.Biomes (script_home) |
| BONES_LEAN_PORT_BUILD_TREELESS_WORLD | RimMandrake.Biomes (script_home) |
| BRONZIUM_DROP_1 | Armoury (proof_defname), neronix17.toolbox (closure) |
| CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES | FlowWorks (script_home) |
| CANON_MATERIALS_BUILD_1 | mandrake.rsw.armoury (proof_cli), neronix17.outerrim.core (proof_cli), Armoury (proof_defname), neronix17.toolbox (closure) |
| COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE | ColdStorage (script_home), Cuisine (script_defname) |
| CONTAGION_SITE_BUILD_SKY_STAYS_CALM | RimMandrake.Biomes (script_home) |
| CRACKEDLANDS_THREE_HEIGHT_FLORA_1 | RimMandrake.Biomes (script_home) |
| CREEP_WEB_HARVEST_LIVE_1 | RimMandrake.Biomes (script_home) |
| DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1 | LuminousPigment (script_home) |
| DEEP_LAYER_BELT_HARNESS_1 | RimMandrake.Biomes (script_home) |
| DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT | FlowWorks (script_home), HugeThings (script_defname) |
| EGROSTER_DEAD_ROWS_PRUNE_SILENT_SKIPS | UtinniPatches (proof_defname), SWBestiary (proof_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE | RimMandrake.Biomes (script_home) |
| EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY | RimMandrake.Biomes (script_home) |
| FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE | RimMandrake.Biomes (script_home) |
| FLAME_STATUES_MOD_BUILD_1 | FlameStatues (proof_defname) |
| FORGE_SKY_PASTURES_1 | RimMandrake.Biomes (script_home) |
| GELATINOUSSLIME_KIT_ART_1 | RimMandrake.Biomes (script_home) |
| GIZKA_STOWAWAY_UNMEASURED_ROWS_1 | GizkaStowaway (script_home), SWBestiary (script_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| GOLD_PANNING_PROVE_THE_COLONIST_STAYS | FlowWorks (proof_cli) |
| GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1 | mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS | neronix17.toolbox (closure) |
| HORIZON_CARAVAN_VANILLA_REFUSES_1 | RimMandrake.Biomes (script_home) |
| HORRORS_RAIDING_FACTION_1 | UtinniPatches (script_home), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| HOSE_SAVELOAD_DIAGNOSE_COMES_BACK_CHANGED | FlowWorks (script_home) |
| HOSE_SL4_FIX_CARRY_NEVER_STAGED | FlowWorks (script_home) |
| JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS | neronix17.toolbox (closure), mandrake.rm.luminouspigment (closure) |
| LEANINGSCRUB_CROWN_MOB_LIVE_1 | RimMandrake.Biomes (script_home) |
| LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 | RimMandrake.Biomes (script_home) |
| LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY | RimMandrake.Biomes (script_home) |
| LONGSHADE_JAWATOW_RECHECK_1 | RimMandrake.Biomes (script_home), UtinniPatches (script_path) |
| LONGSHADE_SCENE_LIVECHECK_1 | RimMandrake.Biomes (script_home) |
| LONGSHADE_STAMPEDE_LIVECHECK_1 | RimMandrake.Biomes (script_home) |
| MAPPRETICK_DIAGNOSE_FULL_LIST_STALL | UtinniPatches (script_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| MIASMA_WARDEN_MOTHER_ART_1 | RimMandrake.Biomes (script_home) |
| MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG | MineShaft (script_home), mandrake.rm.mineshaft (proof_cli), mandrake.rsw.armoury (proof_cli), Armoury (proof_defname), neronix17.toolbox (closure) |
| MODCHECK_DONOR_ENVIRONMENTS_1 | ebsg.framework (proof_cli), adaptive.storage.framework (proof_cli), vanillaexpanded.vfefactory (proof_cli), oskarpotocki.vanillafactionsexpanded.core (proof_cli), neronix17.toolbox (closure) |
| PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES | FlowWorks (script_home) |
| PIT_CAPTURE_FIX_WARDEN_HURT_AT_LIP | FlowWorks (script_home), HugeThings (script_defname) |
| PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH | FlowWorks (script_home) |
| PIT_ESCAPE_PROVE_LADDER_LEFT_DOWN | FlowWorks (script_home) |
| PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES | FlowWorks (script_home) |
| PLASTEEL_AUDIT_EXPLICIT_MINEABLE_LISTS | mandrake.rm.minerals (proof_cli), Minerals (proof_cue) |
| PLAYER_START_SITE_1 | StructureInjectionsRUT (script_home) |
| PLOT_D_BODY_PRUNE_STALE_SEA | FlowWorks (script_home) |
| PUMP_DRAW_FIX_LOSES_A_LEVEL | FlowWorks (proof_cli) |
| PUMP_ON_TANK_FIX_NO_COUPLER | FlowWorks (script_home) |
| PYRELANDS_SHIP_READINESS_1 | RimMandrake.Biomes (script_home) |
| QUARRYSHARE_FIX_ZEROED_GOVERNED_WEIGHTS | ogliss.thewhitecrayon.quarry (proof_cli), mandrake.rm.minerals (proof_cli), Minerals (proof_cue) |
| QUARRY_DIG_FIX_VALIDATED_BUT_NEVER_FINISHES | FlowWorks (proof_cli) |
| QUICKTEST_POLICY_NRE_FULLLIST_1 | MandrakePatches (script_home), mandrake.rm.patches (proof_cue) |
| RECKONING_HISTORYEVENT_REWIRE_OFF_QUESTEND | EggReckoning (proof_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure), mandrake.rm.weathersuite (closure) |
| ROT_FAUNA_KIN_WIRING_1 | mandrake.rut.patches (proof_cli) |
| RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM | nals.facialanimation (proof_cue), neronix17.toolbox (closure), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| SCARLANDS_CHATRAK_LIVE_RERUN_1 | RimMandrake.Biomes (script_home) |
| SCRUB_WILDLIFE_PROVE_NOBODY_CAME | RimMandrake.Biomes (script_home) |
| SHADE_LESSONS_BUILD_WATCH_THE_HERD_CROSS | RimMandrake.Biomes (script_home) |
| SOORRAK_INSTANT_JOB_LOOP_1 | RimMandrake.Biomes (script_home) |
| SPECIES_TRAITS_OVER_APTITUDES_1 | neronix17.toolbox (closure) |
| STARWARS_JUNK_RESKIN_1 | StarWarsPatches (script_home) |
| STILLSAND_CONTENT_LIVE_PROOF_1 | RimMandrake.Biomes (script_home) |
| STILLSAND_GLASS_CHAIN_REMAINDER_1 | RimMandrake.Biomes (script_home) |
| STILLSAND_MUURROK_EMERGENCE_1 | RimMandrake.Biomes (script_home) |
| STILLSAND_RETURN_REMAINDER_1 | RimMandrake.Biomes (script_home), dubwise.dubsbadhygiene.lite (proof_cue), dubwise.dubsbadhygiene.thirst (proof_cue) |
| STILLSAND_ROOF_COVER_EXPOSURE_1 | RimMandrake.Biomes (script_home) |
| SUMP_TAR_FIRE_NETWORK_1 | FlowWorks (script_home) |
| TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING | 7f.alienworlds (proof_cue), 7f.alienworlds.tidallylocked (proof_cue) |
| UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL | FlowWorks (script_home) |
| UNPROVEN_LIVE_LEGS_TRIAGE_1 | RimMandrake.Biomes (proof_cli) |
| VCE_CANFISH_FIX_RESKIN_SKIPS_BILL | mandrake.rsw.cuisine (proof_cli), vanillaexpanded.vcooke (proof_cli) |
| VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT | SolarMirrors (proof_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| VEE_WORLD_RENAME_ONE_STAMP_AT_END | SolarMirrors (script_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| WARCASKET_JUNKER_KINDS_BUILD_1 | mandrake.rm.warcasket (proof_cli), UtinniPatches (proof_defname), mandrake.rm.flowworks (closure), mandrake.rm.luminouspigment (closure) |
| WARSCAR_HOSPICE_DESERTERS_1 | RimMandrake.Biomes (script_home) |
| WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT | Armoury (proof_cli), StarWarsPatches (proof_cli), ResearchRetag (proof_cli), UtinniPatches (proof_cli), Doctrine (proof_cli), LuminousPigment (proof_cli), RimMandrake.Biomes (script_path), neronix17.toolbox (closure) |
| WEEPINGSTONES_NET_FLEEING_FLIER_1 | RimMandrake.Biomes (script_home) |
| WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE | RimMandrake.Biomes (proof_cue) |
| XENO_HEADS_SCENE_PROVE_ALIENS_WEAR_THEM | StarWarsRaces (script_path), neronix17.toolbox (closure) |

## 3 Baseline for criterion 3 (recounted before landing)

`python3 src/RimMandrake/rimflow/relentless_names.py baseline --since 2026-10-30T00:00:00Z --until 2026-11-06T04:00:00Z`
over `/home/mandrake/rm/relentless/live/runs.jsonl`: 912 rows, 737 non-PASS, **141 non-PASS rows with a mod-list cause**
over 33 items and 26 games. By cause: not enabled in modsconfig 49, not in the running load 49, does not cover 18, type not found 15, missing_mod 4, not loaded on this tier 4, wrong_tier 2. The one-week-after count reruns the same command with
`--since <landing> --until <landing + 7 days>`; every new row also carries `env` (the effective mod list and each
inferred addition with its evidence).

