# BENCH_REBOOT_HANDOFF_202611031955 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611030827`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Today's failures were all LEAKS and MISLABELS, not bugs: the clone pool and /tmp filled because nothing deterministic drained them, and 64% of live-game slots since 15:00Z measured nothing (wrong mod tier, harness refusals). Owner's ruling: cleanup and health are deterministic programs, never an agent's memory. Operations owns the health verdict; Relentless only reads it; system items take the next free place, never preempt running work, and content fills places only when every open system item is already being worked (standing_rulings.md, 92fb22cca400). Live-game waste is the headline to watch.

Two helpers were still running at handoff and report only to the dead window: the tmp-cleanup builder (TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP; commits 11312ebfc6, 11e7989519; GPT review under D:\ClaudeWork\rimmandrake\reviews\tmp_scheme_2026-11-03\) and the live-slot waste builder (progress D:\ClaudeWork\rimmandrake\conductor\live_waste_progress.md). Read their commits and progress files; don't wait for a notification. Steve: Kingston C:, numproc 18 live, CSM off, Ethernet 192.168.86.62, wake-on-LAN PROVEN 19:54Z (D:\ClaudeWork\rimmandrake\steve_diag\wol.ps1), BIOS via `shutdown /r /fw`, final BIOS visit done; Hestia/Custos summary in D:\Luke\dev\Hestia\inbox\custos\2026-11-03-stevedesktop-drive-replacement.md.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Cards waiting for him (he asked for them; send them after he says he has looked): (1) the Relentless status-page mockup, D:\ClaudeWork\rimmandrake\conductor\mock_shot.png (sent to his phone) and relentless_view_mock_20261102.html: build it for real, what to change; (2) when to hold ONE looking session (10 items: TITAN_CAMPS, HOSE pipe atlases, PIT_ACCESS, DRAWBRIDGE, THRIXWEAVE, 3 RimPulse widgets, GRAFFITI save, WATER_SCENES d3); (3) when to hold the flyer live-test session (gravship sea-floor flight, skarrin netting / WEEPINGSTONES, steadier flier bodies); (4) ICON_OUTLINE: recommend repainting 9 icons; (5) SANDLION: recommend retiring 6 orphan sprites. Full list: D:\ClaudeWork\rimmandrake\conductor\owner_triage_2026-11-03.md. He wants a recommendation with its reason on every card.
- Steve's router DHCP reservation for the Ethernet MAC D4-5D-64-B5-8D-D1 (192.168.86.62): his Google Home app.
- Nightly selftests: tonight's 03:00 full run is the first measured count after ~38 fixes; report it in the morning brief.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ACC_BIOMES_FIXES_LIVE_RERUN_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `ART_OVERRIDE_FAMILY_SCRIPT_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `ASHKARR_WEATHER_INSTALL_THE_SLEEPING_STORMS` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `BRIDGE_STALL_DIAGNOSTIC_1` — Relentless candidate; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `CANAL_OBJECTS_SHEET_BUILD_POSES_AND_STYLES` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `CANON_MATERIALS_BUILD_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `CANOPY_LAYER_BUILD_ROOF_OF_THE_WORLD` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `CRACKEDLANDS_THREE_HEIGHT_FLORA_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `CREEP_WEB_HARVEST_LIVE_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `DEEPFIRE_FAMILY_SETTINGS_SAVE_LOAD_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `DESSICATED_CORPSES_REDRAW_ONE_BY_ONE` — Relentless queued; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `DONOR_COATS_REDRAW_SIX_HUNDRED_TO_GO` — Relentless queued; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `DONOR_OFF_LOAD_PROVE_AFTER_BENCH` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `FACINGS_REDRAW_NORTHS_ABOUT_FACE` — Relentless queued; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `FLEETWATCH_PAGE_SHRINK_LESS_BASH_MORE_MODS` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `FORGE_SKY_PASTURES_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `GAMECOMP_STALL_HUNT_SEVEN_SECONDS` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `GELATINOUSSLIME_KIT_ART_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `GENERATOR_MODS_PROVE_INERT_AFTER_CREATION` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `GRAFFITI_V1_LIVE_PROOF_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `GRAVSHIP_PEACEFUL_SETTLEMENT_LANDING_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `HEADS_VERIFY_SHRUNK_TO_FIT_THE_HATS` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `HEAVY_TEXTURES_MEASURE_REAL_VRAM` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `HUGETHINGS_TRUNK_ZERO_BLOCKERS_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `ICON_OUTLINE_REPAINT_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `LEANINGSCRUB_CROWN_MOB_LIVE_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `LEANINGSCRUB_SWEETLINE_SHED_LIVE_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `LIVE_VERDICT_BUILD_INFRA_NOT_FAIL` — a live Opus helper is fixing live-slot waste (16/25 UNMEASURED since 15:00Z; did LIVE_MODLIST_ENFORCE_BEFORE_SLOT regress?); NEXT: read D:\ClaudeWork\rimmandrake\conductor\live_waste_progress.md and compare measured share before/after
- `LONGSHADE_SCENE_LIVECHECK_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `LONGSHADE_STAMPEDE_LIVECHECK_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `MAP_AWARENESS_PROVE_ON_A_QUIET_MAP` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `MIASMA_WARDEN_MOTHER_ART_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `MINES_SWAP_RETIRE_SHAFT_ALREADY_DUG` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `NIGHTLY_REDS_FIX_REMAINING_REAL_FAILS` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `OLLOPOM_BEAUTY_VERIFY_DEPLOYED_NOT_SEEN` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `PACK_ANIMALS_RESTORE_EMPTY_SADDLES` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `PYRELANDS_SHIP_READINESS_1` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `RAIL_WALK_PROVE_NOBODY_WALKS_OFF_ANYWAY` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `ROT_MOSS_VERIFY_UNDER_THE_MUSHROOMS` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `RSW_FACES_VERIFY_IN_GAME_BEFORE_SHIM` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `SCARLANDS_CHATRAK_LIVE_RERUN_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `SOORRAK_INSTANT_JOB_LOOP_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STARWARS_JUNK_RESKIN_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STILLSAND_DUNE_GALE_LIVE_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STILLSAND_GLASS_CHAIN_REMAINDER_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STILLSAND_LOOMMA_SUNSTRUCK_SHADE_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STILLSAND_RETURN_REMAINDER_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `STILLSAND_SAND_SWIM_REMAINDER_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `TEXREGEN_UNPROVEN_ASK_THE_SHEETS` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `TIRED_SWIMMER_FIX_UNREACHABLE_SHORE` — Relentless running; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `UNPROVEN_LIVE_LEGS_TRIAGE_1` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WARSCAR_HOSPICE_DESERTERS_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WASTELAND_CONTAGION_PROBE_FIVE_LOOSE_ENDS` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WASTELAND_LIVE_SUITE_FAILS_ACC_BIOMES_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WATER_DEPTH_RESKIN_HE_LOOKS_FIRST` — Relentless not in the Relentless pool; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WATER_SCENES_S5_JUDGE_THIRD_DRAFT` — Relentless held; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WEEPINGSTONES_HANDLER_VANISHES_1` — Relentless game; NEXT: leave it to Relentless; act only if its reading shows it held or circling
- `WORLD_STIPPLE_VERIFY_CALMER_FACES_LOOK` — Relentless checking; NEXT: leave it to Relentless; act only if its reading shows it held or circling

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- /tmp is an 18 GB tmpfs that agent ad-hoc scratch filled to 100%, turning ~58 nightly tests red (see: TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP)
- Trailing state-only commits (lessons, ledger) pinned pool clones forever; places fell to 6/8 (see: POOL_FIX_STATE_COMMITS_PIN_CLONES)
- Relentless's flight gate reads "no flight" as flight and holds items for the owner falsely (see: FLYER_GATE_FIX_NEGATION_READS_AS_FLIGHT)
- robocopy default retries (/R:1000000 /W:30) hung 4 h on a damaged USB stick and blocked a seat restart (filed: lessons, 74e95c1b66)
- bcdboot rebuilds the BCD and silently drops numproc 18 on Steve; re-applied (see: D:\ClaudeWork\rimmandrake\steve_diag\nvme_replacement.md)

## Closed since the last handoff (75)

- `LANDMARK_NAMING_PASS_1` — c1488ce83f841f77edb285fc51cba9f0b9a8936c
- `BIOME_ENRICHMENT_DESERT_WASTELAND_1` — b9cfe1853d661c10d2a9c597a6b5147fde390263
- `FLEETWATCH_PAGE_REPAIR_BLIND_REVIEW_PARTLY` — 93d65bae08b40ef4ba3b45cb5a18250405347c0e
- `NORTHSTAR_VALIDATION_SKILL_1` — 7e1018bda61d9791dc081daaedd300d9f7fe1d96
- `ARTIST_BIOME_INSPIRATION_MOD_1` — 5ed6a4d9d2e24e6244930a27463360865f21b299
- `NORTHSTAR_PARTIAL_GAPS_FILL_1` — 9da1638f66cfdcb4af42af10b5988c22a8ee5fb6
- `FALL_LINE_MUTATOR_PLACEMENT_1` — 69f12111f29f418eaf2dae9fda7dfe0b7a58042e
- `ART_SUBJECT_RESOLVER_1` — 3ce67795593fbc57450881a15791f38c113a59f3
- `OPS_QUEUES_READING_RESTORE_HQXV` — 1b083af2630bbf97b80defda0450c15f43d6c41e
- `ART_VERSION_WRANGLING_1` — d95e4f5c264a23e5d1c99106e95fab468fa2667a
- `MYNOCK_FLIPBOOK_FRAMES_1` — d95e4f5c264a23e5d1c99106e95fab468fa2667a
- `LIVINGBOLT_CORPSE_ART_1` — 655a57911d7ce40c2cd5ca559eade5d8dc0d8388
- `OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU` — 172ec3ac238946c76bc44b163c169af86c2b6827
- `OPS_TIMER_REPAIR_PRXC` — 894b273ef3a0
- `OPS_TIMER_REPAIR_PRXC` — 894b273ef3a0
- `BIOME_GROUP_SIZE_WALK_1` — a166f7c1a7317f144f75388792dd2dc9754a214b
- `NIGHTSIDE_ICE_NEW_LIFE_1` — d1e8cbb8c5c6ebb2ae18313a520991080acee4be
- `SALT_BREAK_FIX_MISSES_POTABLE_SOURCES` — 51921633949bef636fb75023cf652f7615a2c27d
- `TANK_DRINK_FIX_LIQUID_SWAPS_MIDJOB` — 57bb94124e9bbc9b6e31ef631a1ef9124ddf40ac
- `GLOOMCAST_FOLLOW_RECHECK_1` — c8c9e5dd7c6cfbe6583c5f07c5707a72dc90315f
- `CLIFF_SHOT_FIX_DEPENDS_ON_SHOOTER_END` — 4e40481c9b579667616fc1aca19067d6f8326815
- `LASSO_CONFIG_UNSET_1` — 4b546167aa0fbe156c6acce0cea2fe323b8748c4
- `EXTRA_ART_PER_BIOME_COMMISSION_1` — 4a5fdb9e4e5b8c5f46f31bd11d80b1d647bba042
- `BIOME_FLORAFAUNA_ART_REVIEW_1` — 448050353dd446ab472e2e43c6b96a073674d640
- `ROT_CARTOON_VARIANT_REPAINT_1` — ae6c60dfdb35fbaacdcb13b989cab4113d7c37c6
- `DESTROY_BATCH_NEVER_KILLS_PAWNS_1` — 4488d2a00abf068193a9e077634221928a636193
- `BONES_LEAN_PORT_BUILD_TREELESS_WORLD` — a08df74207828c78a5a519262e9fd341aaab61cf
- `TRENCH_COVER_FIX_DECK_ERASES_UNDERPASS` — 71b598ea01981e1845f3626c6e80f5e16f60d3a1
- `ART_SHEETS_SCALE_CELLS_WIDEN_TOO_LATE` — 41e36028f9a47b6ea3aca970b07724653d765265
- `BODY_SPLIT_FIX_FISH_SHARE_SHRINKS` — b44bc53c230b8415bab214eb16b19a86905ce5a3
- `SARLACC_PIT_WIDEN_THE_BIG_ONES` — 2638899c96fc4ec522ce25330f75c3582c3bbda7
- `READOUT_PROOF_FIX_BYPASSES_MOUSEOVER` — 56bd0e0876f199e1a55a7f1130254b309ebe759a
- `MOOKEE_TRADE_ANIMAL_IDENTIFY_1` — 3225e5a1decfb1c9ba67a3357a3898e4c5e7538f
- `OVERFLOW_DROWNING_FIX_NO_WARNING` — 377d0644570e97b050c8c1cdca84e4e71853ac4c
- `SPRINT_KIT_ART_SKETCH_BEFORE_THE_VETO` — 6e84f8f62680a7ba1fbbf70331995069cbc2c973
- `OLD_ART_SHEETS_REBUILD_WITH_SCALE_PANELS` — 1d83909565feb8455a2b084e7fb9c545fa881bb6
- `SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE` — 5b81b8223e3da367c1beb3e1fbb38c0da84fd5ab
- `SUCCULENT_PLANTS_REDRAW_BORROWED_WARDROBE` — 5b81b8223e3da367c1beb3e1fbb38c0da84fd5ab
- `NIGHTLY_REDS_DIAGNOSE_FIFTY_IS_A_CROWD` — d0e160471e
- `DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN` — 08c9d0ff3308175e84b1a39a6a32f2b46857a159
- `DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN` — 08c9d0ff3308175e84b1a39a6a32f2b46857a159
- `DONOR_SUCCULENT_ART_DECIDE_A_STAND_IN` — 08c9d0ff3308175e84b1a39a6a32f2b46857a159
- `FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART` — c7cfe36eb5a347198530107b3d6abfe6aa25d6fe
- `FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART` — c7cfe36eb5a347198530107b3d6abfe6aa25d6fe
- `FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART` — c7cfe36eb5a347198530107b3d6abfe6aa25d6fe
- `FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART` — c7cfe36eb5a347198530107b3d6abfe6aa25d6fe
- `ART_SIZES_AUDIT_AFTER_DONORS_LEAVE` — 937e10dd78e1558bf273881c6fa12c36ddca0425
- `WEIR_TANK_SELFTESTS_FIX_MISSING_PIN_SHAS` — 088a64296078
- `ALPHA_BIOMES_CENSUS_FIX_UNDECIDED_TOKENS` — c5183fdcea
- `COMMISSION_LEDGER_CLEANUP_1` — 4a71c05aa295e08c4796c61a93e6b7247cb08e10
- `REGEN_GAPS_DECIDE_STRAYS_AND_FLYERS` — 5446826a832df58cc1528c5f78d247f3fda6b3c3
- `VEXXITH_USES_SELFTEST_FIX_250S_TIMEOUT` — ed15fefa6d
- `OPS_RELENTLESS_GAME_HOLD_UNSTICK_DRDP` — 08c75f0e71fdf5645d5ce44003b9c51819dc5777
- `CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES` — 53a4897ba80a05f4423c13fe8e0403297d51329f
- `CAULDRON_SOILS_BUILD_DIRT_THAT_BREATHES` — 53a4897ba80a05f4423c13fe8e0403297d51329f
- `TEXREGEN_GAPS_REDRAW_EIGHTEEN_QUEUED` — 859c8c5fe8e98401a222d35d8d0c228192bef3d8
- `TEXREGEN_GAPS_REDRAW_EIGHTEEN_QUEUED` — 859c8c5fe8e98401a222d35d8d0c228192bef3d8
- `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` — 466bd416858f
- `FAUNA_TOLERANCE_NORMALIZATION_1` — 9c2cf869015d
- `FORGE_DHUVVOX_SWARM_REMAINDER_1` — 0140ba1e19ed
- `SARLACC_SEEKER_ROOTING_1` — 81f4689881ff
- `WARLAB_SPECIMENS_DESIGN_BREAKOUT_CHOICE` — 76edd0eccfed
- `SALVAGE_MINIFY_DESIGN_HAULER_OR_SCRAP` — a8c4b8710ac1
- `SHEET_NOTES_FINISH_SEVENTEEN_DEF_HALVES` — 5e214563ebea
- `ROT_REGEN_SHEET_FINISH_SIX_OPTIONS_SERVED` — 6c5ad04c8060
- `DESSICATED_CORPSES_INSTALL_AFTER_PICKS` — b5df068fe4bb
- `CAI_FOG_SILENCE_FORCED_OFF_BY_US` — 7f1145d571e1
- `CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS` — 35986d2a3b15
- `FLIER_LINE_CHECK_FIX_SIDEWAYS_UNSEEN` — 9ef4be7d17d7
- `LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP` — 35f4733453f8
- `FLESHSOP_REDESIGN_AS_WEAPON_SYSTEM` — 02064f927acd
- `TREE_CROWN_MEASURE_FROM_THE_ART` — b8f121b92c713f0fd773ff252454127bc8d20a71
- `LUNGERFRY_DECIDE_WEARS_ZEEVS_COAT` — a464923603
- `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` — 3b7034cfa5f1fc57a62f188673c878f7aa0b2eed
- `DEV_SCRATCH_DIRS_MIGRATE_OFF_LODESTARS_LAWN` — 3b7034cfa5f1fc57a62f188673c878f7aa0b2eed

## Filed and still open (226) — the next seat's queue

- `FEVERWOOD_LURE_TUNE_AFTER_A_REAL_RAID` — Retune the two-front lure's numbers against a real colony's lure use
- `FLOWWORKS_SELFTEST_FIX_TWO_STRAY_REDS` — Two red FlowWorks C# selftest cases (pond capacity, pipe riser rim)
- `PROOF_SHA_FIX_DEPLOYS_NOTHING_TWICE` — HARNESS: a live round on a built sha that touched no shippable mod file (a proof-only fix) deploys nothing and checks no running-load gap, so the proo
- `MURROWBULB_ICON_REDRAW_STILL_A_POTATO` — RM_RawMurrowbulb (src/RimMandrake/Stillsand/Defs/ThingDefs_Plants/RM_Murrowbulb.xml) wears vanilla Things/Item/Resource/PlantFoodRaw/Potatoes, marked 
- `FLEETWATCH_UNIT_REWIRE_RUNS_A_STALE_SEAT` — rm-fleetwatch.service runs fleet_refresh.py from /home/mandrake/rm/bench, a seat working clone with no sync timer (17 behind on 2026-11-03): fixes lan
- `FLEETWATCH_UNIT_REWIRE_RUNS_A_STALE_SEAT` — rm-fleetwatch.service runs fleet_refresh.py from /home/mandrake/rm/bench, a seat working clone with no sync timer (17 behind on 2026-11-03): fixes lan
- `FLEETWATCH_PARTS_PRUNE_HOARDS_EVERY_ROW` — Fleet Watch board's parts collection keeps every row ever written (211 docs on 2026-11-03, 3 list pages); each version sync reads them all (~0.37 USD)
- `FLEETWATCH_PARTS_PRUNE_HOARDS_EVERY_ROW` — Fleet Watch board's parts collection keeps every row ever written (211 docs on 2026-11-03, 3 list pages); each version sync reads them all (~0.37 USD)
- `PROOFS_CHECK_FIX_PIRATE_ROWS_UNINVITED` — Selftest 'proofs' check fails on infrastructure/state/live_proofs/NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS.rows.json, committed as evidence in 3e568fab2a;
- `PROOFS_CHECK_FIX_PIRATE_ROWS_UNINVITED` — Selftest 'proofs' check fails on infrastructure/state/live_proofs/NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS.rows.json, committed as evidence in 3e568fab2a;
- `FORGE_CHECKS_FIX_PASSING_ON_WRONG_NUMBER` — TheForge validation.py: flyers_carry_flight_stat accepts any positive stat value once MaxFlightTime is named (MaxFlightTime=0 passes); dhoggur health/
- `FORGE_CHECKS_FIX_PASSING_ON_WRONG_NUMBER` — TheForge validation.py: flyers_carry_flight_stat accepts any positive stat value once MaxFlightTime is named (MaxFlightTime=0 passes); dhoggur health/
- `FORGE_CHECKS_FIX_PASSING_ON_WRONG_NUMBER` — TheForge validation.py: flyers_carry_flight_stat accepts any positive stat value once MaxFlightTime is named (MaxFlightTime=0 passes); dhoggur health/
- `WM_PLASTEEL_RESTORE_FIX_FORGE_FORGETS` — WreckedMachines: setting_plasteelAlloyEnabled_drives_def row plasteelAlloyEnabled_restores_the_shipped_def FAILs live (modcheck run WreckedMachines 20
- `WM_PLASTEEL_RESTORE_FIX_FORGE_FORGETS` — WreckedMachines: setting_plasteelAlloyEnabled_drives_def row plasteelAlloyEnabled_restores_the_shipped_def FAILs live (modcheck run WreckedMachines 20
- `WM_PLASTEEL_RESTORE_FIX_FORGE_FORGETS` — WreckedMachines: setting_plasteelAlloyEnabled_drives_def row plasteelAlloyEnabled_restores_the_shipped_def FAILs live (modcheck run WreckedMachines 20
- `RECEDE_EXPIRY_FIX_ONE_CLOCK_MANY_FLOODS` — Recede aftermath: one expiry clock for many floods' irqit and salvage (per-batch deadlines)
- `RECEDE_EXPIRY_FIX_ONE_CLOCK_MANY_FLOODS` — Recede aftermath: one expiry clock for many floods' irqit and salvage (per-batch deadlines)
- `RECEDE_EXPIRY_FIX_ONE_CLOCK_MANY_FLOODS` — Recede aftermath: one expiry clock for many floods' irqit and salvage (per-batch deadlines)
- `RECEDE_EXPIRY_FIX_ONE_CLOCK_MANY_FLOODS` — Recede aftermath: one expiry clock for many floods' irqit and salvage (per-batch deadlines)
- `RECEDE_EXPIRY_FIX_ONE_CLOCK_MANY_FLOODS` — Recede aftermath: one expiry clock for many floods' irqit and salvage (per-batch deadlines)
- `SETTLEMENT_SHIPVISIT_BUILD_VANILLA_SAYS_RAID` — Peaceful gravship landing on a full faction Settlement (not a Site): vanilla ArriveNewMap always calls AffectRelationsOnAttacked for a Settlement, and
- `SETTLEMENT_SHIPVISIT_BUILD_VANILLA_SAYS_RAID` — Peaceful gravship landing on a full faction Settlement (not a Site): vanilla ArriveNewMap always calls AffectRelationsOnAttacked for a Settlement, and
- `SKILL_VALIDATOR_FIX_CRIES_WOLF_AT_PHANTOMS` — skills/validate_skills.py (bare) exits 1 on 6 jawa/ names; 4 are deliberate 'this tool does not exist' mentions (rimbridge-companion PHANTOMS line 200
- `SW_TEMPLATES_REWIRE_DONORS_LEFT_TOWN` — StructureInjectionsSW templates place 6 ThingDefs no loaded mod has: retarget in the .lua sources and re-export
- `REDFOG_SELFTEST_REPAIR_FOG_OF_WAR` — selftest_starwarspatches_semantics RED on main: weather defs RSW_SW_RedFog and RSW_SW_RedFoggyRain defined in StarWarsPatches/Defs/WeatherDefs/SWDeser
- `JUNK_RESKIN_REDO_REDRAW_NINE_LIVES` — Redraw the Star Wars junk slots that shipped empty: judge REDO on AncientTank_07, AncientWarwalkerShell_05, AncientMegaCannonBarrel_02 (both takes), A
- `RENDER_BINDINGS_DECIDE_ORPHANS_AWAIT_PARENTS` — Pick the subject (or no-subject) for the 349 render families on the binding sheet (src/RimMandrake/Utils/art/binding_sheet.py build; enact --by agent 
- `SARLACC_STAGEONE_MERGE_TWO_WORMS_ONE_THROAT` — Merge the two Stage-I young-sarlacc defs (RSW_SarlaccSwimmer, RM_Gulloth) into one; keep the swallow/changed-return trigger and both incidents
- `SARLACC_STAGEONE_MERGE_TWO_WORMS_ONE_THROAT` — Merge the two Stage-I young-sarlacc defs (RSW_SarlaccSwimmer, RM_Gulloth) into one; keep the swallow/changed-return trigger and both incidents
- `SOHL_BUILD_ONE_MOVE_TOTAL` — Sohl: the one-move animal, dormant, one lunge, spent (defs + C#)
- `FRISSIM_BUILD_WAITS_FOR_THAW` — Frissim: flightless inclusion insects released by thaw (defs + C#)
- `WYRMLET_BUILD_SHIVVEN_HAND_ME_DOWNS` — Wyrmlet: the apex young, foreshadow rung of the ladder (defs + C#)
- `DHORRUMAK_BUILD_BIGGEST_LAST` — Dhorrumak: the apex ice wyrm, sustained-heat breach set-piece (defs + C#)
- `HESSARUND_BUILD_JUST_A_RIDGE` — Hessarund: the living ridge, a mineable landform yielding catalyst crust (defs)
- `SAALLEN_BUILD_BLISTERS_ON_CUE` — Saallen: seam crust that blisters when warmed and marks the breach ring (defs + C#)
- `OOLM_BUILD_ONE_BODY_MANY_LOBES` — Oolm: clonal mineable lobes, one body per colony (defs + C#)
- `NESHKOLL_BUILD_POINTS_AT_LEAKS` — Neshkoll: frost fans that lean toward the colony's heat leaks (C#)
- `ICEKEPT_DEAD_BUILD_CUT_OUT_COLD` — Ice-kept dead: bodies held in clear ice, cut out for corpse and gear (defs + C#)
- `CAULDRON_NETTLE_OFFARM_BUILD_TWO_OF_THREE` — Cauldron A4 third arm: a live component proving nettle gardens stop with condensateGardensEnabled off
- `BROOD_GIZMO_TOOL_BUILD_CLICKS_GO_NOWHERE` — Generic JawaBench gizmo-invoke tool + brood tally read + FeverWood components proving BROOD_RANSOM A3 tally and A4 gift
- `CATHEDRAL_BASEFINISH_ROWS_BUILD_MAP_EXISTS` — RustCathedral validation components for BASE_FINISH A5-A9 on a live_site.py --biome RM_RustCathedral map
- `FORGE_VOICE_ROWS_FINISH_HALF_SUNG` — Extend TheForge voices/dormancy components: all four phase cues, sustainer, dhuvvox seal + count invariant (ENRICHMENT_QUICKTEST A3/A4 remainder)
- `SCALD_STACK_TEXTURES_DELETE_NOBODY_HOME` — Delete 6 orphan stack-texture folders src/RimMandrake/TerminalBiomes/Textures/Things/Item/Resource/{RM_EkkelCatch,RM_KarrashCatch,RM_MuddalCatch,RM_Sa
- `SCALD_STACK_TEXTURES_DELETE_NOBODY_HOME` — Delete 6 orphan stack-texture folders src/RimMandrake/TerminalBiomes/Textures/Things/Item/Resource/{RM_EkkelCatch,RM_KarrashCatch,RM_MuddalCatch,RM_Sa
- `SCALD_STACK_TEXTURES_DELETE_NOBODY_HOME` — Delete 6 orphan stack-texture folders src/RimMandrake/TerminalBiomes/Textures/Things/Item/Resource/{RM_EkkelCatch,RM_KarrashCatch,RM_MuddalCatch,RM_Sa
- `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` — pulse-deploy checkout got writer edits (CANON_MATERIALS_BUILD_1 files and ledger shards, ~12:38Z 11-03, all already on origin), so rm-pulse-update fai
- `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` — pulse-deploy checkout got writer edits (CANON_MATERIALS_BUILD_1 files and ledger shards, ~12:38Z 11-03, all already on origin), so rm-pulse-update fai
- `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` — pulse-deploy checkout got writer edits (CANON_MATERIALS_BUILD_1 files and ledger shards, ~12:38Z 11-03, all already on origin), so rm-pulse-update fai
- `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` — pulse-deploy checkout got writer edits (CANON_MATERIALS_BUILD_1 files and ledger shards, ~12:38Z 11-03, all already on origin), so rm-pulse-update fai
- `EXTRA_LOOKS_WIRE_AS_THEY_TRICKLE_IN` — Wire each commissioned extra look (design/RimMandrake/extra_art_commission/commission.csv: female -> femaleGraphicData, female pack, variant -> PawnKi
- `VIOLETWIMPLE_TILEGRID_FIX_CAPS_ON_PARADE` — VioletWimple_A.png (src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/VioletWimple) is a regular 2x4 grid of identical caps — reads as a tiled 
- `RESTORE_LEAKS_FIX_EIGHT_NEW_STRAYS` — selftest_proof_restore_check red: 8 new proof restore-leak hits (LeaningScrub, LuminousPigment, RimProperty)
- `STALLPROBE_CURTICK_FIX_ONE_RED_LINE` — selftest_static_game_state.py is RED on origin/main: JawaBenchStallProbe.cs:32 static int CurTick (from 472474378b, BRIDGE_STALL_DIAGNOSTIC_1) is not 
- `XART_FAILS_DIAGNOSE_TENTH_SECOND_RENDERS` — 39 commissioned extra-art jobs (xart_*) sit in D:\ClaudeWork\rimmandrake\artpipe\failed after a 0.12 s 'generated' then 'validated fail' (e.g. xart_RM
- `RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS` — Relentless supervisor ticks grew from 1-2 min (2026-11-02) to 3-7 min with 9/11/15 min outliers (2026-11-03 journal, rm-relentless.service); find the 
- `RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS` — Relentless supervisor ticks grew from 1-2 min (2026-11-02) to 3-7 min with 9/11/15 min outliers (2026-11-03 journal, rm-relentless.service); find the 
- `RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS` — Relentless supervisor ticks grew from 1-2 min (2026-11-02) to 3-7 min with 9/11/15 min outliers (2026-11-03 journal, rm-relentless.service); find the 
- `RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS` — Relentless supervisor ticks grew from 1-2 min (2026-11-02) to 3-7 min with 9/11/15 min outliers (2026-11-03 journal, rm-relentless.service); find the 
- `MODCHECK_CLEARAREA_FIX_PAWNS_STILL_LOITER` — modcheck suite.clear_area (src/RimMandrake/Utils/modcheck/suite.py:295) clears the test area with jawa/destroy_batch categories=All, which never remov
- `STARWARSRACES_SUITE_FIX_STILL_SAYS_NO_DLL` — src/RimStarWars/StarWarsRaces/validation.py SCOPE says the mod has no compiled code and suite.toggles=[]; since 41a57e24f3 it ships a DLL with Mod Set
- `SUMPMOUSE_ART_INSTALL_STILL_SQUEAKS` — Two followed-note redraws never installed: RM_SumpMouse still wears the plain mouse (owner: 'less mouse-like and more alien'; renders thesump_SumpMous
- `NSJUDGE_TMPDIR_FIX_TMPFS_FULL_OF_MUTANTS` — northstar judge_cli stages captures in tempfile.mkdtemp (/tmp tmpfs, 18G, 97% full of workers' mutation copies) and dies ENOSPC; stage under agent sto
- `SETTINGS_SCREENS_FIX_FOUR_STALE_TABLES` — selftest_settings_screens.py red at 0fa427bbe2 on four screens not touched by SARLACC_PIT_WIDEN_THE_BIG_ONES: BlueDesert (12 groups vs 10), CrackedLan
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `KIT_ART_INSTALL_FISHED_FROM_THE_WORKERS` — Install the 10 judge-kept biome-sprint kit lines (art-store shas in infrastructure/state/delegated/2026-11-03/kit_art_veto.json): fit each raw 1254px 
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — artpiped codex channel flaps: 'sandbox not ready: shared sandbox state is not current (cannot read Password last set for the codex sandbox users (net.
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `CREATURE_SIZES_JUDGE_THIRTY_NINE_OFF_CURVE` — True-scale judge sitting for the 37 animals art_size_audit.py lists REVIEW (drawn <0.5x or >2.1x vanilla's body->drawSize curve, e.g. RM_Immu 0.30 cel
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `TMPFS_SCRATCH_PRUNE_FIFTH_LESSON_SAME_DISK` — WSL /tmp (18G tmpfs) fills with agent scratch and kills live proofs: modcheck deploy's biomes_compose mkdtemp hit ENOSPC on 4 runs 2026-11-03T17:28Z (
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `SADDLES_FREE_TIER_VERIFY_HOLD_THE_HUTTS` — Free tier live: on a list WITHOUT UtinniPatches (RimMandrake.Biomes, all five DLC) a vanilla trader caravan can be generated for RM_WeepingStones and 
- `POOL_FIX_STATE_COMMITS_PIN_CLONES` — Relentless pool full: a worker's trailing lesson/ledger commit pinned its parked clone; scratch_clone alarmed stranded on belt-owned clones; default s
- `NIGHTLY_REDS_FIX_REMAINING_REAL_FAILS` — After /tmp freed + clone synced, ~35 of the 57 nightly FAILs still red (rimflow lease/built/incident/reconcile cluster, paint_list, art_checks, one_pa
- `NIGHTLY_REDS_FIX_REMAINING_REAL_FAILS` — After /tmp freed + clone synced, ~35 of the 57 nightly FAILs still red (rimflow lease/built/incident/reconcile cluster, paint_list, art_checks, one_pa
- `TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP` — /tmp (18G tmpfs) filled to 100% with agents' mutation scratch (cm_mut, wlmut, gwm, ~15 GB), turning the nightly selftests red; make mutation tools use
- `FACING_NORMVIEW_FIX_SHRINKS_SNAKES_TO_PEAS` — facing_backlog drv.py norm_view scales every new N/S to east's HEIGHT; for long low bodies drawn high-angle (Dragonsnake) a correct rear view shrinks 
- `FACING_NORMVIEW_FIX_SHRINKS_SNAKES_TO_PEAS` — facing_backlog drv.py norm_view scales every new N/S to east's HEIGHT; for long low bodies drawn high-angle (Dragonsnake) a correct rear view shrinks 
- `FACING_NORMVIEW_FIX_SHRINKS_SNAKES_TO_PEAS` — facing_backlog drv.py norm_view scales every new N/S to east's HEIGHT; for long low bodies drawn high-angle (Dragonsnake) a correct rear view shrinks 
- `READOUT_SELFTEST_MEND_PATTERN_LOST_ITS_LINE` — FlowWorks SelfTest Readout_two_numbers_and_the_limitless_mark is RED: RewireChecks.cs:203 greps RM_NorthstarProofs.cs for 'return "OK " + (eng.DepthRe
- `READOUT_SELFTEST_MEND_PATTERN_LOST_ITS_LINE` — FlowWorks SelfTest Readout_two_numbers_and_the_limitless_mark is RED: RewireChecks.cs:203 greps RM_NorthstarProofs.cs for 'return "OK " + (eng.DepthRe
- `READOUT_SELFTEST_MEND_PATTERN_LOST_ITS_LINE` — FlowWorks SelfTest Readout_two_numbers_and_the_limitless_mark is RED: RewireChecks.cs:203 greps RM_NorthstarProofs.cs for 'return "OK " + (eng.DepthRe
- `LIVE_VERDICT_BUILD_INFRA_NOT_FAIL` — Three-way live verdict PASS/FAIL/INFRA with a pre-proof health check (bridge reachable from the driving interpreter, deployed hash = built hash, site 
- `CALL_DEADLINES_ENFORCE_130_OPEN_ENDED` — Lint: every blocking subprocess/external call carries a timeout (130 of 325 measured without); robocopy bounded /R /W plus a total deadline. Design: d
- `RED_COP_BUILD_NO_ORPHAN_REDS` — Every new nightly selftest red auto-files a top-priority item with a deadline; an overdue red alarms whether owned or not. Design: design/RimMandrake/
- `STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF` — jawa/static_call ThingID resolver splits off trailing digits of defNames ending in a digit
- `TITAN_WALL_CRUSH_DIAGNOSE_WOOD_WALL_SHRUGS` — Titan RoofWallProbe holes thin roof but wall HP unchanged
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `SWEETLINE_CANOPY_REDRAW_TRUNKS_THAT_EARN_IT` — Paint real trunk + canopy art for RM_SweetlineTree (14 letters): today's pools are script-derived stand-ins (canopy_art.py: geometric crown-base cut, 
- `PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF` — Pipeline SLOs + error budget: when spent, Relentless takes only pipeline-repair items until healthy again; postmortems must ship a class guard test. D
- `PROOF_SETTINGS_RESTORE_FIX_NINE_LEAKS` — Nine proof scripts set a mod setting and do not restore it on throw (proof_restore_check)
- `PAINT_LIST_FIX_STALE_COREFRAMEWORK_EDGE` — PAINT list: biomesteam.coreframework has no class ref left to justify it
- `BRIDGETOOLS_DLL_REBUILD_THREE_TOOLS_MISSING` — Rebuild the JawaBench DLL: 3 source tools absent from it
- `DECIDE_MUT_GOLDEN_FIX_TMPDIR_BOUND` — selftest_role_launch_decide_mut golden embeds the off-switch path under TMPDIR: passes standalone, FAILs (decide_off_switch_and_window, decide_off_swi
- `SWDESERT_WEATHER_DECIDE_REDFOG_DEAD_CONTENT` — RSW_SW_RedFog and RSW_SW_RedFoggyRain are attached to no biome since the donor retirement (5afbec097e): attach or delete
- `ARENA_BANK_REBUILD_MISSING_FIVE_ROWS` — arena bank lacks RP_ tasks for 5 prompt-rewrite items (SHADOW_INGEST_FIX_MISSING_SNAPSHOT, SHADOW_SHEET_WIDEN_REPLACED_KEPT_ART, SHADOW_VIEW_ROWS_FIX_
- `FLYER_VARIANTS_FIX_RULED_COLUMNS_MOVED` — selftest_flyer_variants: RM_FleetFlier C and RM_Murrelith D/E columns changed after his ruling; ruling rows do not carry his words: re-ask or re-point
- `ART_CHECKS_FIX_OUTLINE_SEVEN_FLAGGED` — art_checks outline_coherence flags 7 sprites (>5): Bolotaur N/E, Emberscythe, FurnaceBeast, OrrayPack, Ullai, Zeer: retune thresholds or fix art
- `QUICKTEST_FRESH_FIX_OLD_GAME_PASSES` — prove_quicktest_world.py exits 0 on an already-Playing game: start_debug_game_ready refuses ('A game is already loaded.', success:false after 280 s) a
- `QUICKTEST_FRESH_FIX_OLD_GAME_PASSES` — prove_quicktest_world.py exits 0 on an already-Playing game: start_debug_game_ready refuses ('A game is already loaded.', success:false after 280 s) a
- `QUICKTEST_FRESH_FIX_OLD_GAME_PASSES` — prove_quicktest_world.py exits 0 on an already-Playing game: start_debug_game_ready refuses ('A game is already loaded.', success:false after 280 s) a
- `STEVE_SHORTCUTS_RESTORE_AFTER_DEFENDER` — Defender on SteveDesktop quarantined ~240 .lnk shortcuts on 2026-10-30 as Trojan:Win32/WinLNK.KH!MTB (6 detection records, all one threat id 214783309
- `RESOURCE_SIM_BUILD_WAITS_FOR_REAL_DATA` — Resource model (disk, /tmp tmpfs, 16-clone pool, 70 GB cap) fitted to >=7 days of real readings (scratch_reap records, pool readings, the new /tmp ala
- `LIVE_SLOTS_MEASURE_NOT_REFUSE_IN_SLOT` — First slice of LIVE_VERDICT_BUILD_INFRA_NOT_FAIL: a live run the running game cannot serve (mods not in the running load, FINAL clause on a small tier
- `IDLE_BRINGBACK_FIX_RESTART_ROWS_EMPTY` — selftest_idle_bringback: 17 checks fail (restart rows empty, kill timing, RAISE FIRST line missing); near relentless.py which another helper is editin
- `SCRUB_WILDLIFE_FIX_Z4_Z5_FINGERPRINTS` — selftest_scrub_wildlife_zero_paths: Z4 FaunaNorm_Law5_Tolerance.xml replaces native stats; Z5 RM_WarscarMod.cs and RM_TheRotMod.cs changed since revie
- `FLYER_GATE_FIX_NEGATION_READS_AS_FLIGHT` — relentless_live flyer_re matches negations: COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE A6 says 'set down 12 cells east on the same map (no flight)' and 
- `READOUT_CHECK_FIX_STALE_AFTER_PROOF_REWIRE` — FlowWorks SelfTest Readout_two_numbers_and_the_limitless_mark fails: RewireChecks.cs:203 still expects RM_NorthstarProofs 'return "OK " + (eng.DepthRe

## Commits

```
a64d9bf5b0 conversations: catch-up 23 record(s)
80cc3d87e4 ledger: relentless supervisor
9d62493c0b ledger: ops_watch alarm(s) note:RELENTLESS_GAME_HOLD_IDLE:relentless.game_hold_idle_min, note:TIMER_FAILED:timers.failed_units
ced246b524 TIRED_SWIMMER_FIX_UNREACHABLE_SHORE: file READOUT_CHECK_FIX_STALE_AFTER_PROOF_REWIRE (stock suite red on an unrelated readout check)
9fb97e22cd BRIDGE_STALL_DIAGNOSTIC_1: review the stall probe's static CurTick (static_game_state green)
f573a80751 SEAT_MEMORY_STANDARD_FALLBACK_1: tmp.mount masked; agent steps wait for next WSL restart
e1cd00c273 TIRED_SWIMMER_FIX_UNREACHABLE_SHORE: review mark for selftest_swim_shore_reach.py
9f86a12b59 TIRED_SWIMMER_FIX_UNREACHABLE_SHORE: commit the shore-search selftest wrapper the contract names
644a2995e5 ledger: relentless supervisor
e32dacf262 COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE: note on FLYER_GATE_FIX_NEGATION_READS_AS_FLIGHT (title hit)
11e7989519 TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP: review mark for run_tmp.py (GPT round 4, consult-20261103-112125-713550)
11312ebfc6 TMP_SCRATCH_ENFORCE_MUTANTS_CLEAN_UP: per-run TMPDIR, a /tmp backstop, /tmp pressure and alarm
b13046e692 owner triage 2026-11-03: 62 needs=owner items triaged (stale 4, delegated 41, his 17)
575e51cecd JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS: review marks for the shallows proof
5e14fee421 JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS: staged brine-cell live proof + offline verdict test
1dc250ae25 TEXREGEN_UNPROVEN_ASK_THE_SHEETS: review marks for unproven_adjudicate + selftest
c18dbc6e0b TEXREGEN_UNPROVEN_ASK_THE_SHEETS: adjudicate all 563 no-record pictures by the commit that brought their bytes in
ee70cfba29 MOUNTAINS2_PLAN_DEPLOY_805_TILES_PACKED: pin base biome + settlement-tile hashes in the proof
2f0f240711 ledger: relentless supervisor
c6c72a49d5 lessons: settle clock from run start; books_stale alien dirt
... 675 more: git log --oneline e056a4f63f..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-03T19:44:13Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/art/events/BENCH.jsonl   Relentless/helpers (seat BENCH art events)
 M infrastructure/state/ledger/events/BENCH.jsonl   this window + helpers (ledger shard)
 M infrastructure/state/ledger/events/OWNER.jsonl   owner-authority events (bridge/game)
 M infrastructure/state/ledger/events/RUNNER.jsonl   RUNNER seat, not this window
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   Relentless FlowWorks worker, not this window
?? cards.json   unknown earlier window, left untouched
?? shortcuts.ps1.txt   Steve-restore helper (Defender shortcut rebuild), scratch
```

