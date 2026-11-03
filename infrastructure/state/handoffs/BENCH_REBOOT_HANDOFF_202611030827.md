# BENCH_REBOOT_HANDOFF_202611030827 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611020411`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Owner is asleep; his order 2026-11-02 21:40 PST: *"Please keep the work going!"* Re-arm the night check (CronCreate, ~35 min: relentless reading, journal, live measured share since 05:40Z, ops alarms; one bounded helper per class of waste; never touch Steve). FOUNDRY is RETIRED (owner card 2026-11-02, "Retire it"): file everything --for BENCH; items bucket Relentless/Designer/Conductor/Operations.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Steve (SteveDesktop) does not boot yet.** Samsung removed; Kingston SNV3S1000G in M.2_2 gives 0xc000000e (BCD still names the Samsung). Owner does the USB repair TOMORROW himself (F8 → USB → Repair → Command Prompt → bcdboot). Full state + steps: `D:\ClaudeWork\rimmandrake\steve_diag\nvme_replacement.md` (2026-11-02 night section). After he boots: confirm C: on Kingston, disable CSM, reagentc rebuild, measure POST (STEVE_POST_TAME_MEMORY_RETRAIN), sshd/Tailscale/Backblaze.
- **Relentless status-page mockup** awaits his reaction: `D:\ClaudeWork\rimmandrake\conductor\relentless_view_mock_20261102.html`. His spec: by mod (+ one non-mod list), # working / # to go, hot = recently finished / in progress / stuck, player-POV descriptions. Blind reader found 5 fixes (needs-you undercount, UTC/PST date, "works" stretched, jargon, install state unknown); needs mod-membership + installed-in-game data.
- Archmagi D: NVMe corrected PCIe errors rising (DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ARTIST_BIOME_INSPIRATION_MOD_1` — - LIVE_MODLIST_ENFORCE_BEFORE_SLOT -- filed, not started (window drained before the helper could launch); NEXT: launch one opus helper via detached_helper.py on it (6/28 live runs wasted on mods absent from the game).
- STEVE (no item) -- owner repairs boot via USB tomorrow; NEXT: when he says booted, run the post-boot checks listed in nvme_replacement.md.
- `ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show ATMOSBASE_PROOF_FIX_UNLIT_LEAVES_DARK_LAMP`)
- `BIOME_ENRICHMENT_DESERT_WASTELAND_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show BIOME_ENRICHMENT_DESERT_WASTELAND_1`)
- `BIOME_TIER_CLEANUP_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show BIOME_TIER_CLEANUP_1`)
- `BIOME_WORLD_SWITCH_WAVE_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show BIOME_WORLD_SWITCH_WAVE_1`)
- `BLUEDESERT_FLORA_PLANT_REFUSAL_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show BLUEDESERT_FLORA_PLANT_REFUSAL_1`)
- `BLUEDESERT_GPT_ENRICHMENT_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show BLUEDESERT_GPT_ENRICHMENT_1`)
- `CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show CAULDRON_TRUNK_DEPOSITS_DESIGN_CRYSTAL_FANS`)
- `COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE`)
- `CONTAGION_SITE_BUILD_SKY_STAYS_CALM` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show CONTAGION_SITE_BUILD_SKY_STAYS_CALM`)
- `DEEP_LAYER_BELT_HARNESS_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show DEEP_LAYER_BELT_HARNESS_1`)
- `DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT`)
- `EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show EGROWTH_SAVELOAD_PROVE_DICT_SCRIBE_SHARE`)
- `EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY`)
- `FAUNA_TOLERANCE_NORMALIZATION_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FAUNA_TOLERANCE_NORMALIZATION_1`)
- `FEVERWOOD_TWO_FRONT_LURE_TUNING_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FEVERWOOD_TWO_FRONT_LURE_TUNING_1`)
- `FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE`)
- `FLESHSOP_REDESIGN_AS_WEAPON_SYSTEM` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FLESHSOP_REDESIGN_AS_WEAPON_SYSTEM`)
- `FLIER_LINE_CHECK_FIX_SIDEWAYS_UNSEEN` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FLIER_LINE_CHECK_FIX_SIDEWAYS_UNSEEN`)
- `FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE`)
- `GIZKA_STOWAWAY_UNMEASURED_ROWS_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show GIZKA_STOWAWAY_UNMEASURED_ROWS_1`)
- `GRAFFITI_NORTHSTAR_GREEN_FULL_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show GRAFFITI_NORTHSTAR_GREEN_FULL_1`)
- `GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS`)
- `GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show GSS_TREE_RECONCILE_FRESH_EYES_VS_OLD`)
- `HORIZON_CARAVAN_VANILLA_REFUSES_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show HORIZON_CARAVAN_VANILLA_REFUSES_1`)
- `HORRORS_RAIDING_FACTION_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show HORRORS_RAIDING_FACTION_1`)
- `JAWABENCH_DESTROY_PAWNS_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show JAWABENCH_DESTROY_PAWNS_1`)
- `LANDMARK_NAMING_PASS_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show LANDMARK_NAMING_PASS_1`)
- `LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY`)
- `LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE`)
- `LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP`)
- `MAPPRETICK_DIAGNOSE_FULL_LIST_STALL` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show MAPPRETICK_DIAGNOSE_FULL_LIST_STALL`)
- `MASS_VALIDATION_LADDER_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show MASS_VALIDATION_LADDER_1`)
- `MODCHECK_DONOR_ENVIRONMENTS_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show MODCHECK_DONOR_ENVIRONMENTS_1`)
- `MODCHECK_ULTRAFAST_CLOCK_STALL_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show MODCHECK_ULTRAFAST_CLOCK_STALL_1`)
- `OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show OPS_RELENTLESS_LIVE_MEASURE_RESTORE_LRPU`)
- `PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES`)
- `PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES`)
- `PLANET_ATMOSPHERE_CLOUD_COST_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PLANET_ATMOSPHERE_CLOUD_COST_1`)
- `PLAYER_START_SITE_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PLAYER_START_SITE_1`)
- `PLOT_D_BODY_PRUNE_STALE_SEA` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PLOT_D_BODY_PRUNE_STALE_SEA`)
- `PUMP_ON_TANK_FIX_NO_COUPLER` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show PUMP_ON_TANK_FIX_NO_COUPLER`)
- `QUICKTEST_POLICY_NRE_FULLLIST_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show QUICKTEST_POLICY_NRE_FULLLIST_1`)
- `RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show RIVERS_ROADS_REDESIGN_WORTH_LOOKING_AT`)
- `RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS`)
- `SCRUB_WILDLIFE_PROVE_NOBODY_CAME` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SCRUB_WILDLIFE_PROVE_NOBODY_CAME`)
- `SEABED_DESCENT_ASCENT_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SEABED_DESCENT_ASCENT_1`)
- `SETTLEMENT_VERBS_WAVE_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SETTLEMENT_VERBS_WAVE_1`)
- `SPECIES_TRAITS_OVER_APTITUDES_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SPECIES_TRAITS_OVER_APTITUDES_1`)
- `STILLSAND_MUURROK_EMERGENCE_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show STILLSAND_MUURROK_EMERGENCE_1`)
- `SUMP_GLASSWALK_SPEED_RATIO_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SUMP_GLASSWALK_SPEED_RATIO_1`)
- `SUMP_TAR_FIRE_NETWORK_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show SUMP_TAR_FIRE_NETWORK_1`)
- `TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show TIDAL_LOCK_FIX_PRESET_NAME_WAS_MISSING`)
- `TITANIC_BODYSIZE_TEST_RACE_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show TITANIC_BODYSIZE_TEST_RACE_1`)
- `VANILLA_BEAST_EXCISION_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show VANILLA_BEAST_EXCISION_1`)
- `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL`)
- `WEEPINGSTONES_NET_FLEEING_FLIER_1` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show WEEPINGSTONES_NET_FLEEING_FLIER_1`)
- `WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show WORLD_DECALS_BUILD_ATLAS_PIPELINE_ONCE`)
- `WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR` — in the Relentless route (BENCH lease is Relentless's); NEXT: leave it to Relentless (`relentless.py show WORLD_NULLTEX_FLOOD_HUNT_STACKLESS_SO_FAR`)

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Live-run share 11% → ~43-64% after a2365bebdc + f04151f434; the game-hold class was a live_iter hold kept after FAIL while the worker ran offline (filed: lessons 20261103T071147Z). A Conductor window over 200k tokens refuses new helpers: launch via detached_helper.py (see: CLOSEOUT_TRAP_FIX_HELPERS_ALWAYS_ALIVE).

## Closed since the last handoff (98)

- `CELL_RECT_SHOT_FIX_COLONIST_BAR_PHOTOBOMBS` — 5f5c01c49f51f16f0a8cd5c1883cb383cf256e2c
- `CONCEPT_TREE_VET_UNTIL_ZERO_FINDINGS` — 550bc610bc41377370012af0879a9745e1e557fe
- `AMEND_HOOK_HARDEN_SWEPT_A_NEIGHBOUR` — 9fd7d703c3bff5adfaa9d1a43acf3f3c2c76d815
- `PACK_OVERLAYS_BUILD_SHARED_SADDLEBAGS` — f34e30a3bd52553f4bab6d45a2aaf74506230954
- `FLIER_FRAMES_FILL_FIVE_GHOST_FLOCKS` — 7cb9cc7a2cd8b8abaedc70f54307eece74e0f8ae
- `PAUSE_ARG_FIX_PAUSED_NEVER_PAUSED` — db6a40cedd6b6f03ef24a06887110825c3107181
- `ASHPULSE_READERS_PRUNE_NOBODY_LEFT` — 7165b2f734377c94ae3350120cddd9846894c590
- `SUSPENSION_PROOF_FIX_EMPTY_ARG_NO_METHOD` — 038a7fbefa0008eaaa4f124d3f9dccc958490b38
- `VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY` — 9d5b089d5f320bd66d25affd5934a21392f9d4ec
- `WALK_SAVE_SILENCE_ABSENT_BIOME_OBJECTS` — a57da3caac9cec075e06fcea4f513895a643982c
- `HOT_RELEASE_FIX_OWN_WET_TERRAIN` — 106f8fe79db8856b496da4006dad8ae5b16ad01e
- `PIPE_ATLAS_REBUILD_OTHER_LOOKS_KINK` — f8e3b6f1b1671ea4a3bb41d12522bb83f7eae22f
- `FLUFF_ASKS_DECIDE_EIGHT_UNDER_VETO` — e6055a28742d04b00a3d14989dc58f61cce772cd
- `FIRE_SCAN_DIAGNOSE_BIG_BURN_COST` — 7efbf823a14405a101519d10940ef1b795b7ea8b
- `OPS_TIMERS_REVIVE_1EEB` — ce5b30485d1091f0a91459b782b34ac9449880eb
- `PUMP_SOURCE_FIX_REJECTS_PARTIAL_DRAW` — 95ef0066c953947f8019ce416dcacb352340312c
- `LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST` — e22b5e432bf42bbc42264036bf4aea32df93ad8b
- `NATURAL_SLIME_DIAGNOSE_NEVER_SLIPS` — 567b22fad99acbaaa9ef388b1699e474d3b420f4
- `OPS_RELENTLESS_UNSTICK_XARX` — 374b4770b0771db84fb429855aee1696f842c436
- `OPS_STEVE_UNSTICK_VHRP` — 87551b29f0e9e207a9aa660be5e69db7cf11b1ea
- `OPS_RELENTLESS_READING_RESTORE_IUUR` — f5298a3f61b0ee2c76902f99c4e6e37295237246
- `SCRATCH_CLONES_RESCUE_FIVE_OUTAGE_SURVIVORS` — 03e4074cfec2961cbb6aef1f622b29265709fb3e
- `WALLED_COPIES_REPAIR_LEAK_RETURNS_BY_EIGHT` — 52b1f26e7d83
- `WALLED_COPIES_REPAIR_LEAK_RETURNS_BY_EIGHT` — 52b1f26e7d83
- `FLEETWATCH_REFRESH_BUILD_OUTLIVES_ITS_WINDOW` — f5a0ac05fbaa
- `OPS_ROLE_DIAGNOSE_STARVED_AT_FOUR_RUNS` — 307feed8ee6d
- `OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC` — 9f0f5d3a8f1731091f18de56b054ef61965d9b03
- `LANDFORMS_PROBE_REPLACE_OR_KEEP_EXPERIMENT` — 7a664f794facaeb0670ecbeb1a32dcb559e9039e
- `RELENTLESS_SLOTS_UNSTICK_BLOCKED_PUT_DOWN` — cdec858bf6c344c6e39cc1b8da5f32597c0c5820
- `FLEETWATCH_PAGE_SHRINK_LESS_BASH_MORE_MODS` — b21d62b9ae
- `WEATHERSUITE_DEPLOY_MAST_LEAVES_THE_BUILDING` — c0868e628faa4db0365f9e2e779aa66587259ae5
- `FLEETWATCH_PAGE_REPAIR_BLIND_REVIEW_PARTLY` — c02f8cd1a4ac
- `WORLD_LABELS_RESTORE_SIZES_MIRROR_WAS_OURS` — dc21cc165ca92eda9646f997c157856f76948b4f
- `EGROWTH_DISABLE_FIX_BLOATED_PLANTS_STAY` — 9516a7cfadcc02f319202d2ca0457345bee6023c
- `PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS` — 50f4ffb8e3a5
- `WORLD_MUTATORS_PRUNE_28K_STOWAWAYS` — 35c7a73ed446a5de2821108f10c2d590431a20d1
- `WORLD_PATHS_VERIFY_WATER_FINALLY_WET` — 00cbc23e700dec681f80e2b47019bf9abe3db5df
- `WORLD_RIVERS_REPAIR_DOWNHILL_AT_LAST` — 8ad08a119b10f00e63f40ae8d656a2649860d9e2
- `RIVER_BUILD_FIX_IN_PLACE_SWEEPS_STATIONS` — 4f8274d85acfe81539c3bec49fae645b806a429c
- `TANK_BOTTLE_FILL_FIX_IGNORES_STOCK_TARGET` — 90a0aad62c9a712627c1e9fcd93ca9f54483a62e
- `POND_OUTLET_FIX_REJECTS_FRACTIONAL_ROOM` — c9767326904a390451143d19ec5774aff2fff718
- `RECESSION_SCAN_TAME_RERUN_PER_CANDIDATE` — e04172a4feb9138ce691b2bbce0a42acbb9055cc
- `LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW` — 425f78e6868654b4e2c60383f2fab2be124fcbd2
- `FILL_IN_DESIGNATION_FIX_SCAN_INVALIDATED` — a882cc11a2e1edca96d73ea86d3ddc28449337c9
- `RELENTLESS_QUEUE_UNSTICK_SEVEN_WAIT_ON_ONE` — 3fb07976365b
- `RELENTLESS_LIVE_FIX_GAME_UP_NOTHING_MEASURED` — 4e52a32fd0beb5a73636cbeb7bca20f00c87cfdc
- `TOKEN_LIMITS_TAME_BARK_NO_BITE` — bbaccde0b098fe8ec788d0c6b60a96f3cd2d346f
- `PORTABLE_LADDER_FIX_EW_LIES_ALONG_WALL` — 5f8455b7175aba4cab829457c9d5e3ec8ae3547b
- `PORTABLE_LADDER_FIX_EW_LIES_ALONG_WALL` — 5f8455b7175aba4cab829457c9d5e3ec8ae3547b
- `PORTABLE_LADDER_FIX_EW_LIES_ALONG_WALL` — 5f8455b7175aba4cab829457c9d5e3ec8ae3547b
- `PORTABLE_LADDER_FIX_EW_LIES_ALONG_WALL` — 5f8455b7175aba4cab829457c9d5e3ec8ae3547b
- `DEHYDRATION_FIX_STAYS_WHEN_THIRST_OFF` — 0415752fd33114b5b95e8234ab66d5dda8fa3d63
- `DEHYDRATION_FIX_STAYS_WHEN_THIRST_OFF` — 0415752fd33114b5b95e8234ab66d5dda8fa3d63
- `EGROWTH_BURST_FIX_NEVERDOWNS_AVERAGES` — 81e4e7282cfc889798495066e69b07b7e6b63734
- `SPIRE_DUNGEONS_MERGE_DARK_TOWER` — f64b973f23df00a55561608338c85b33054a7aec
- `GUBBRA_GOURD_FIX_WONT_SELECT` — a268ec52ab50e84c82ce88cb898855e1dd7c5815
- `GUBBRA_GOURD_FIX_WONT_SELECT` — a268ec52ab50e84c82ce88cb898855e1dd7c5815
- `BOOKS_STALE_FIX_OPS_CANNOT_SEE_IT` — c5a80db3604a
- `BOOKS_JAM_FIX_CODE_REVIEW_SHARD_SHUFFLES` — c5a80db3604a
- `BOOKS_STALE_FIX_ART_SHARD_REORDER` — c5a80db3604a
- `IMMERSION_DAMAGE_WIRE_NEVER_APPLIED` — 1f6c68bb89a616d20d6e9aba60ec749496908eef
- `LEVEL_PERF_PROOF_SHRINK_TO_FIT_BUDGET` — c129550e8795c7b541874276229540eb1aa433aa
- `FOREIGN_GUARD_PROVE_FLAT_KEPT` — 975aa2a0c16d6850a8994fa77747ad8de26bc8d4
- `MYNOCK_REGEN_INSTALL_NEEDS_GRAPHIC_MULTI` — fa2e6f138b40df302ba53fdd77b4fa05927ee2d3
- `DECISIONS_ORPHANS_PRUNE_NO_SNAPSHOT` — f49267361b7ddced5a096bf106655bd85519193d
- `PROOF_SPOILED_RUNS_BUILD_NO_BLANKET_GREEN` — 1661c3fd8b22d077a644046cbd534ef5522b4d7f
- `SERIES_STOP_FIX_RENAMED_DEF_ESCAPES` — 1cec24a030e138a51ccbc8696f03110c140bed5b
- `ATMOSPHERIC_BASE_HARDEN_SMALL_LAMP_COUNTS` — 7edd675e57a47e016df0f857da1f43d6257745de
- `MODERN_FLANGES_POLISH_DARKER_THAN_THE_BODY` — 12a6f0dd10feb97b108a66bbc0222943834e4db0
- `FOREIGN_GUARD_WIDEN_MIRROR_CROP` — cf5b07eb3b93fe74b69f777b361a328be91cc418
- `LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT` — a2365bebdc76
- `LIVE_CUT_CRITERION_ENFORCE_AT_IMPLEMENT` — a2365bebdc76
- `LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT` — a2365bebdc76
- `LIVE_STALE_HARDEN_CAUGHT_BEFORE_SLOT` — a2365bebdc76
- `LIVE_EXIT2_FIX_DEFECT_AFTER_TWO_GAMES` — a2365bebdc76
- `LIVE_EXIT2_FIX_DEFECT_AFTER_TWO_GAMES` — a2365bebdc76
- `LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD` — a2365bebdc76
- `LIVE_REFUSAL_SILENCE_SAME_TEXT_HELD` — a2365bebdc76
- `NS_CAPTURE_DOWN_FIX_OWN_PIRATE_TRIPS` — 3e568fab2a0c0a7786e018e9197bba8c8d7d2b67
- `CAULDRON_ROSTER_BOUNDARY_RECONCILE_PATCH` — 8454f352342f01f1492677e6346bf3f4a2712586
- `SCALDHIDE_R1_DESIGN_NEW_CREATURE` — 87e99c15840d6e3908403f637b129581729d62f6
- `ROUND_SERIES_FIX_SAME_SECOND_RESTART` — de308d481de12d6b237ddbecb15026e2c415f526
- `VEXXISS_VARIANT_WIRING_VET_REVIEW` — d4964759565a4655c60149e6f7b69cbd433b23eb
- `WORLD_SEA_FACES_INSTALL_PICKED_LOOKS` — 15e6748fabc3c647ee450694d90d76f1ce302d29
- `TERRAIN_DRINK_FIX_SMALL_POND_REFUSED` — 0f58221844abcc11ebb9a3584a4b5637fa8df0e1
- `TANK_SHADOW_DIAGNOSE_DRIFTS_OFF_THE_SKID` — 58194141b5dfdc1cef0d6bdddea3ab489a80d217
- `OPS_ARTPIPE_UNSTICK_RBLV` — 8a7879296b
- `SWB_TWINS_DEDUPE_STILLSAND` — 3cff04f22476130ee1e112e6c8113ccbb4418da7
- `MODCHECK_DIAGNOSE_DRIVER_DIES_MID_SETFOG` — cf7807e42daf6a8e181a2d58efa94f5bdeebb6a8
- `THERMOSTAT_FIX_IGNORES_SUBNOTCH_LIQUID` — 819c5a8b3aae98ac9178142fd03483a46ca3bc13
- `VALIDATION_V2_IDENTITY_WIRE_READS_ZERO` — 2e256d9b3c5c83bab078b6c93163daff28a6c5d2
- `COLD_LOAD_RUN_SHEET_4` — b4593761c49ec30412bda7999df01aa11acf998f
- `RELENTLESS_GAME_HOLD_UNSTICK_IDLE_LIVE_ITER` — f04151f434a7
- `WET_CELL_CENSUS_FIX_SHEETS_READ_DRY` — a26ae714b1893a7f509bb241a1a9a4ede9105dbe
- `FLOOD_EXPIRY_FIX_FULL_CELL_TRAVERSAL` — bbea0548b71ed88d0fa977bc1572d8228279641b
- `INHABITED_AUGMENTATION_BUILD_1` — 27f3566e69eaf24fc29dc2c352b5f1182c464764
- `FAUNA_LORE_DIVERSIFICATION_1` — 7be4ad5022941d4b923756da2618668e36fe584a
- `FEVERWOOD_ANT_HIVE_DUNGEON_1` — f21d4f3e3219dc763284c31ecdd1cf85709e5b2f

## Filed and still open (127) — the next seat's queue

- `SETTINGS_AUDIT_REFRESH_ONE_GROUP_TOO_MANY` — selftest_settings_screens.py RED on origin/main 7ec1b04602: WreckedMachines 5 groups found, expected 4; WasteRun 4 found, expected 3 (screens gained a
- `BLINDCHECK_PROVE_VERDICTS_EATEN_BY_DISK` — Re-run the blind checks for HOT_RELEASE_FIX_OWN_WET_TERRAIN and WALK_SAVE_SILENCE_ABSENT_BIOME_OBJECTS: their checker outputs were zeroed by the 2026-
- `INCIDENT_SELFTEST_FIX_RED_BEFORE_ANYONE_CAME` — selftest_incident.py FAILS at 872b3647c4 (before any 2026-11-02 Relentless change): 'a replay watch alarm joins the ledger' — the opened work_belt inc
- `RELENTLESS_GAME_FIX_HOLD_LIFT_FORGETS_GAME` — relentless step(): when the owner lifts a hold, needs_back calls ledger_needs(item, 'offline') — for a game-mode item (needs bridge/game-up/deploy) th
- `RELENTLESS_GAME_PROVE_REIMPLEMENT_AFTER_FAIL` — relentless_game: after a game_fail the item is ledger 'built' while a new offline worker runs; its next blind PASS calls rimflow implemented again on 
- `WALLBOX_SHRINK_STILL_SHIPS_WHOLE_TREE` — relentless_wall.make_box still exports the whole tree (~3.3 GB, checkout-index of every tracked file minus tree_exclude) once per check; after df0c153
- `HELPERCLONE_FIX_STALE_FENCE_OF_A_STRANGER` — A detached helper's reused relentless clone kept .git/relentless.json of LIVE_PROOFS_POPULATE_CLEAN_BUILDS_FIRST gen 7, so the pre-push fence refused 
- `BLOCKFRONTIER_FIX_ROLE_UNIT_LEAKS_IN` — selftest_block_frontier t_base_reader_tolerates_until is red on origin/main when run from a detached helper unit: fixture events carry role_unit (stam
- `SCRATCH_CLONES_PRUNE_LANDED_DEAD_WEIGHT` — Prune landed stale clones: ~/rm/scratch/BENCH/{ra_s09,transfer,agent-improve-20261101-192155,restart-now,review_b} (all landed; dirt is ledger line re
- `MIASMA_DRAKE_FIX_GRASS_GONE_MISSING` — Miasma static check fails: RM_DecayDrake.xml:116 references RM_GlowingGrass, which no Miasma def file defines (python3 src/RimMandrake/Miasma/validati
- `SETTINGS_SCREENS_FIX_TWO_OUTGREW_AUDIT` — selftest_settings_screens.py red on main: WreckedMachines has 5 groups (audit expects 4), WasteRun 4 (expects 3); update the audit or the screens (see
- `PUMP_OUTFLOW_FIX_PART_SOURCE_HOGS_DOOR` — [MINOR] Pump outflow branch burns the outflow's turn when only the source is short
- `HOSE_SELFTEST_FIX_TWO_PATTERNS_GONE_STALE` — [MINOR] Two FlowWorks hose selftest call-site patterns fail on main
- `CRACKEDLANDS_DUALCROP_FIX_VEF_NEVER_INVITED` — Live 16-mod load 2026-11-02 (no VEF): Player.log line 56, first exception: 'Exception loading def from file RM_CrackedLands_DonorPorts.xml: Could not 
- `CRACKEDLANDS_DUALCROP_FIX_VEF_NEVER_INVITED` — Live 16-mod load 2026-11-02 (no VEF): Player.log line 56, first exception: 'Exception loading def from file RM_CrackedLands_DonorPorts.xml: Could not 
- `LEVELPORTS_FIX_BUDGET_STARVES_BACK_ROW` — RM_Levelling: when one network component's open ends (up to 16, by reel id) walk more than WalkBudget (120000 squares) in a cycle, hoseCursor restarts
- `THIRSTCHECK_FIX_DECOMPILE_NOT_HOME` — ThirstChecks.cs:381 reads D:\Luke\dev\reference\rimworld-decompiled\RimWorld\Pawn_NeedsTracker.cs, absent on Archmagi, so every run_selftests --only s
- `SUITE_REGISTRY_WIDEN_FORTY_SEVEN_STRAYS` — live_queue jobs.suite_mods() reads modcheck_status.json: 47 on-disk suites (validation.py with suite=) are never in the situational pass; decide which
- `PATCHES_EFFECTFLOOR_FIX_FIVE_DONORS_NAPPING` — selftest_mandrakepatches 'shipped fixes vs the load-14 dump' FAILs on HEAD: floor checked>=15 but only 12 checkable with 5 donor mods inactive on the 
- `PATCHES_EFFECTFLOOR_FIX_FIVE_DONORS_NAPPING` — selftest_mandrakepatches 'shipped fixes vs the load-14 dump' FAILs on HEAD: floor checked>=15 but only 12 checkable with 5 donor mods inactive on the 
- `GREENTIDE_SUITE_HARDEN_PASSES_ON_FAITH` — Greentide validation.py can pass on faith (GPT review 2026-11-02): (1) _comp clears upstream_failed after a setup _unmeasured, so mire/swallow/frenzy_
- `DETACHED_LAUNCH_FIX_SAME_SECOND_CLOBBER` — detached_helper launch: a second launch on the same item in the same second gets the same unit name, fails, and overwrites the RUNNING helper's record
- `DETACHED_LAUNCH_FIX_SAME_SECOND_CLOBBER` — detached_helper launch: a second launch on the same item in the same second gets the same unit name, fails, and overwrites the RUNNING helper's record
- `SELFTEST_DECIDE_MUT_REPAIR_RUNNER_TMP_PATH` — selftest_role_launch_decide_mut.py: decide_off_switch_and_window + decide_off_switch_on_event_run_is_not_spent FAIL under run_selftests.py only (golde
- `OPS_RUNCOST_SHRINK_ALARM_RUN_PAST_BUDGET` — Operations alarm run rm-role-operations-1793638866 (2026-11-02 17:01Z, 6 revisited incidents) cost 597,578 weighted (raw 3.48M) against its 450k advis
- `LEDGER_UNION_DEDUPE_PUBLISH_DOUBLED_LINES` — merge=union on ledger shards writes byte-identical duplicate lines on every publish rebase (268 in BENCH.jsonl; evidence D:\ClaudeWork\rimmandrake\rel
- `RELENTLESS_BREAKER_DIAGNOSE_UNREADABLE_TREE` — relentless breaker.json carries fault 'checkout 567b22fad99a: fatal: unable to read tree' — a clone or books object store missing a tree; find which c
- `RELENTLESS_START_SILENCE_REFUSED_RETRY_LOOP` — relentless retries start on EGROWTH_SWELL_DECIDE_FLIP_OR_GROAN every ~30 min (24 start_refused since 2026-11-01T22:47Z, store journal.jsonl): rimflow 
- `SHIPFALL_SWITCH_ENFORCE_LIGHTS_LEFT_ON` — LongShade validation.py STATIC FAIL: Shipfall Commons MapComponentTick ignores modEnabled (runs with Long Shade off) — RM_ShipfallCommons.cs:141
- `FLEETWATCH_WRITE_SHRINK_TOKENS_TO_NEAR_ZERO` — After the redesign looks good: Fleet Watch refresh writes the board from deterministic Python, cutting the ~52k tokens per written run (headless claud
- `RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS` — Relentless sets needs=owner on EVERY hold (proof_weak, spend, game) via ledger_needs_owner (relentless.py ~2284): 14 of 49 owner-routed items 2026-11-
- `PROOF_TIERS_WIDEN_FOUR_FULL_LIST_HOLDOUTS` — Four places still assume the full mod list (per small-lists-first ruling): FOUNDRY preflight_flowworks P-O4, prove_null_thingclass_live --list default
- `FLEETWATCH_MODS_PRUNE_GONE_STILL_WAITING` — Fleet Watch never deletes a mod group gone from the gather (e.g. Cross-mod after the rolling window drops it): its old doc stays up to 7 days with a s
- `FLEETWATCH_PROOFSUM_FIX_BLIND_FAIL_MISSED` — Fleet Watch mod proof summary reads only Relentless checks: a newer ledger-only blind FAIL shows as a cross on its task while the mod summary still sa
- `WORLD_HIGHWAY_TUNE_NAVY_IN_DISGUISE` — Ancient highway fill (0.08,0.08,0.085) renders navy (~48,56,80) under the planet light; warm it like the Stone layer so it reads asphalt, not water
- `EGROWTH_FLUSH_PROVE_HAS_ONLY_A_TREE` — ExplosiveGrowth top_flush has no subject: the only Flush roster row (RSW_Plant_HydenockTree_Wild) is a tree, whose forced top is TreeBurst, so flush_p
- `THORNHOLD_TETHER_FIX_WALKS_THROUGH_THE_STALL` — Stall freeze is broken for the Thornhold: RM_CompHomeTether replaces the Stall's Wait_Wander with an InterruptForced Goto home (RM_CompHomeTether.cs:9
- `THORNHOLD_TETHER_FIX_WALKS_THROUGH_THE_STALL` — Stall freeze is broken for the Thornhold: RM_CompHomeTether replaces the Stall's Wait_Wander with an InterruptForced Goto home (RM_CompHomeTether.cs:9
- `OPERATIONS_RUN_SHRINK_ATE_SIX_HUNDRED_K` — Operations run rm-role-operations-1793638866 (2026-11-02 ~17:05Z) used 597578 weighted tokens (raw 3476530) against a 450000 advisory budget: find wha
- `OPERATIONS_RUN_SHRINK_ATE_SIX_HUNDRED_K` — Operations run rm-role-operations-1793638866 (2026-11-02 ~17:05Z) used 597578 weighted tokens (raw 3476530) against a 450000 advisory budget: find wha
- `BOTTLE_FILL_FIX_SMALL_POND_TOO` — [MINOR] Bottle-fill search refuses a limited pond under one level (1000 L) though a bottle costs a fraction; RM_LiquidBottleUtility.cs search uses ex.
- `FLEETWATCH_ROW_FIX_BLOCKED_STILL_BUILDING` — Fleet Watch shows WAVE1_FIXES_DEPLOY_BEFORE_THE_CUT as Building + 'circling: no progress' alarm 8 h after Relentless blocked it (18:23Z) and its worke
- `RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY` — Relentless staffs deploy items it cannot finish: workers are forbidden deploy_custom_mods --apply ('supervisor deploys') but the supervisor never depl
- `BUILT_OLD_READER_FIX_LEASE_VERB_UNKNOWN` — selftest_built_old_reader red: t_old_model_replays_without_crashing - old clone model errors unknown verb 'lease'
- `FOCUS_CAP_FIX_STAGE_PLACES_FAILS` — selftest_focus_cap red: stage_places live path not held to the number; does not admit the one under it
- `HELPER_RECEIPTS_FIX_KILL_READS_CRASH` — selftest_helper_receipts red: a kill with no record reads as 'before the last boot: the restart, or a quit or crash earlier'
- `PRESCREEN_FIX_AUDITS_FILE_SCHEMA` — selftest_audit_prescreen red (UNMEASURED): p.json.audits.jsonl missing then line 1 breaks audits.schema.json (ts, sha, run required)
- `ALPHA_BIOMES_FIX_UNDECIDED_TOKENS` — selftest_alpha_biomes_census red: UNDECIDED_TOKEN AB_Fern/AB_Grass/AB_Grass_Polluted in selftest_donor_retire_standin.py
- `ART_CHECKS_FIX_OUTLINE_COHERENCE_SEVEN` — selftest_art_checks red: outline_coherence flags 7 files (>5): BolotaurPack_north, Bolotaur_east, Emberscythe_east, FurnaceBeast_north, OrrayPack_nort
- `ART_RULINGS_FIX_FLYER_COLUMN_BASELINE` — selftest_flyer_variants + selftest_drawn_art_ruled red: RM_FleetFlier C south ruling column mismatch; baseline rows RSW_Eopie east/north now pass, rem
- `CLASS_REFS_FIX_UNRESOLVED_PIPESYSTEM` — selftest_lint_def_type_refs + selftest_paint_list red: UNRESOLVED PipeSystem.Building_Pipe in Absorbed_Kotorcore_VEF; biomesteam.coreframework CLOSURE
- `STARWARS_FIX_WEATHER_DEFS_LEATHER` — selftest_starwarspatches_semantics + selftest_leather_factors red: weather_defs_are_all_attached check FAIL in chain; whole-block Replace break not ca
- `RUN_MUTATION_FIX_AUDIT_TARGETS_MISSING` — selftest_run_mutation red: audit_targets - selftests importing target modules missing from TARGETS (arbiter_tiers, dispatcher, ...)
- `ONE_PATH_SEAM_FIX_LOCALSLOW_LITERAL` — selftest_one_path_seam red: no_new_localslow_literal_outside_the_seam (6/7)
- `ARENA_REWRITES_FIX_FIVE_ROWS_UNBANKED` — selftest_arena_prompt_rewrites red: every row measured against the bank (27 of 32); SHADOW_VIEW_ROWS_FIX_MERGED_UNLABELLED, TPS_VERDICT_FIX_WINDOW_LAB
- `EXPLOSIVEGROWTH_FIX_PROBE_PLANT_MOVED` — selftest_explosivegrowth_archetype_seed red: PoisonPlantTallGrass is not on the RUT_BlueDesert sheet
- `SELFTEST_FIX_SIX_TIMEOUTS_AT_240S` — CRASH timeout 240s on rerun: atmosphericbase_kernel, vexxith_uses, wasterun_kernel, spire_one_building, coldstorage; idle_bringback FAIL 155s
- `WATER_TERRAINS_FIX_EIGHT_NAME_NO_LIQUID` — selftest_water_terrains_name_liquid red: 8 Water-tagged terrain(s) name no liquid (drunk as Potable FreshWater)
- `FLOWWORKS_GPT_B_FIX_ACID_FILL_TIERS` — selftest_flowworks_gpt_b red: swim patch hazardous fill tiers - RM_Fill_AcidWater_Brim/Half/Superdeep/Trace unmarked (hits 48)
- `LIVEPROOFS_WRAPPERS_EXCISE_OUT_OF_DIR` — live_proofs/ holds PLANET_ATMOSPHERE_CLOUD_COST_1_live.py and _selftest.py (2a00378d0e); selftest_relentless_live_round t_proofs_file requires .txt/.c
- `RELENTLESS_CRITERIA_SYNC_AFTER_RETIER` — GRAFFITI_NORTHSTAR_GREEN_FULL_1's ledger holds pre-retier A1/A2 text; live_proofs/<ID>.criteria now differs, so every live round REFUSES (re-tiered). 
- `CAULDRON_TRUNK_DEPOSITS_BUILD_SWEAT_SHOWS` — Cauldron: build the scab+crystal-fan coat on thornwood trunks (design 2026-11-02)
- `CAULDRON_FLECKS_FIX_NUGGETS_IN_MIDAIR` — Cauldron: assay fleck overlays float ~31% off the trunk and miss V3 palette
- `LIVE_PROOFS_DIR_FIX_PY_WRAPPER_RED` — selftest_relentless_live_round t_proofs_file is red on origin/main: infrastructure/state/live_proofs/PLANET_ATMOSPHERE_CLOUD_COST_1_live.py is a .py i
- `L1_DONOR_SELFTEST_FIX_READS_A_GHOST` — selftest_l1_donor_off_round FAILs 'donor rename names read for the save row' in a fresh clone: l1_donor_off_round.SARLACC_RENAMES reads Transient/phas
- `ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS` — Two arteval outputs are centre-cropped foreign renders (Dustflutter r1 east, Peeper r3 south)
- `RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM` — Full-file code review owed after 2026-11-03 fixes (c5a80db3, 7c16acb1, 72954d63): ops_watch.py, relentless.py, their selftests, ops_watch_rules.json, 
- `RAWSHADE_BUILD_SKIRT_COMES_DOWN` — Build RM_Rawshade (Scaldhide render C): defs, art install, living-canopy Burn shelter
- `COUPLER_GLINTS_POLISH_PINK_OUTLIVED_RED` — Modern blue: pink/salmon specular dashes left on Coupler (and pump) highlights — desaturate toward steel
- `COUPLER_GLINTS_POLISH_PINK_OUTLIVED_RED` — Modern blue: pink/salmon specular dashes left on Coupler (and pump) highlights — desaturate toward steel
- `DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW` — Archmagi D: NVMe (Kingston SFYRD4000G, PCI bus 3, root port 0:6.3 Intel AE4E) logs WHEA-17 corrected PCIe AER errors, rising: 10-26:6 10-29:1 10-30:9 
- `DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW` — Archmagi D: NVMe (Kingston SFYRD4000G, PCI bus 3, root port 0:6.3 Intel AE4E) logs WHEA-17 corrected PCIe AER errors, rising: 10-26:6 10-29:1 10-30:9 
- `NIGHTLY_SELFTESTS_RESCUE_RED_SINCE_FOREVER` — Nightly full selftest sweep (rm-selftests-nightly, Transient/selftests_nightly.log) has been RED every logged night; FAIL count climbed 16/851 -> 34/9
- `NIGHTLY_SELFTESTS_RESCUE_RED_SINCE_FOREVER` — Nightly full selftest sweep (rm-selftests-nightly, Transient/selftests_nightly.log) has been RED every logged night; FAIL count climbed 16/851 -> 34/9
- `VOLTMAW_TIER_MIGRATE_SPARKS_INCLUDED` — RSW_Vozzik (voltmaw, AA_TetraSlug port) is NOT a twin of RM_Vozzik: owner 2026-10-04 gave it the Rust Cathedral and a synthetic redraw, RM_Vozzik the 
- `VOLTMAW_TIER_MIGRATE_SPARKS_INCLUDED` — RSW_Vozzik (voltmaw, AA_TetraSlug port) is NOT a twin of RM_Vozzik: owner 2026-10-04 gave it the Rust Cathedral and a synthetic redraw, RM_Vozzik the 
- `SANDLION_ART_RETIRE_OWNER_KEPT_ORPHANS` — 6 owner-kept PNGs at SWBestiary Textures/Things/Pawn/Animal/AA_SandLion (live+dessicated, 3 facings) are orphans since RSW_SandLion was retired into R
- `SANDLION_ART_RETIRE_OWNER_KEPT_ORPHANS` — 6 owner-kept PNGs at SWBestiary Textures/Things/Pawn/Animal/AA_SandLion (live+dessicated, 3 facings) are orphans since RSW_SandLion was retired into R
- `IDLE_BRINGBACK_SELFTEST_FIX_SHARD_HOLD` — selftest_idle_bringback red at HEAD: every bring-back held by 'ledger shard unpublished: UNMEASURED: not a git repository' (fixture clone is no git re
- `IDLE_BRINGBACK_SELFTEST_FIX_SHARD_HOLD` — selftest_idle_bringback red at HEAD: every bring-back held by 'ledger shard unpublished: UNMEASURED: not a git repository' (fixture clone is no git re
- `PITCAPTURE_DIAGNOSE_PRISONER_FLAG_BACKSLIDES` — pit_prison_room capture_down_from_the_lip FAIL (valid) again in testq J20261101T083051Z-386617 (runner bd365feabd): {'held': 'True', 'prisoner': 'Fals
- `QUEUE_STALL_ALARM_FINISH_THE_STRAGGLERS` — Wire the remaining claim/lease queues (arena, fleet, replay watchers) into ops_watch's 'queues' family (stalled_min, fixed alarm id per queue, blind a
- `QUEUE_STALL_ALARM_FINISH_THE_STRAGGLERS` — Wire the remaining claim/lease queues (arena, fleet, replay watchers) into ops_watch's 'queues' family (stalled_min, fixed alarm id per queue, blind a
- `SEA_FILMS_FIX_SPHERE_ASSUMED_WHOLE` — RM_WorldLook.BuildSea sizes its shore/deep films by 4 pi r^2 / TilesCount, which over-states tile spacing on a partial-coverage planet (bands come out
- `SEA_FILMS_FIX_SPHERE_ASSUMED_WHOLE` — RM_WorldLook.BuildSea sizes its shore/deep films by 4 pi r^2 / TilesCount, which over-states tile spacing on a partial-coverage planet (bands come out
- `STEVE_POST_TAME_MEMORY_RETRAIN` — SteveDesktop POST takes ~293 s (measured 11-01) and up to ~10 min at the logo before DEL is accepted (owner, 2026-11-02). Likely DDR5 4-DIMM (~128 GB)
- `STEVE_POST_TAME_MEMORY_RETRAIN` — SteveDesktop POST takes ~293 s (measured 11-01) and up to ~10 min at the logo before DEL is accepted (owner, 2026-11-02). Likely DDR5 4-DIMM (~128 GB)
- `RELENTLESS_SELFTESTS_FIX_STANDING_REDS` — selftest_relentless_live red at origin (RUT_Reckoning_Rumor measured case + main running_mods); selftest_relentless_live_round red (PLANET_ATMOSPHERE_
- `RELENTLESS_SELFTESTS_FIX_STANDING_REDS` — selftest_relentless_live red at origin (RUT_Reckoning_Rumor measured case + main running_mods); selftest_relentless_live_round red (PLANET_ATMOSPHERE_
- `TWINLABELS_DEDUPE_SIXTEEN_DOPPELGANGERS` — label_collision_check.py exits 1 on 16 cast RM_/RSW_ twin pairs sharing a label (e.g. RM_TunnelSnake/RSW_TunnelSnake, RM_RustNipperJuv/RSW_RustNipperJ
- `FOUNDRY_LITERALS_EXCISE_FROM_CODE` — Excise FOUNDRY seat literals: ops_watch.py, l1_batch_manifest.py:196, v3_ready.py:549, v3_cutover.py:47, helper_budget/slot_allocator, install_wt_seat
- `FOUNDRY_CLONE_UNITS_MIGRATE_TO_BENCH` — Re-home rm-mirror, rm-codebase-health, rm-artpiped off /home/mandrake/rm/foundry; then check the foundry clone's 2 dirty files and land unlanded work
- `LIVE_PROOFS_STRAY_PRUNE_RED_SELFTEST` — selftest_relentless_live_round red on real data: stray live_proofs files (PLANET_ATMOSPHERE_CLOUD_COST_1_live.py, NS_CAPT*, .criteria)
- `LIVE_PROOF_LINES_FILL_FOR_BUILT` — Built items with live-level criteria but no live-proof line wait forever as 'no proof' in Relentless game_prove (ex-FOUNDRY acceptance lane)
- `FINDINGS_FOLD_REVIVE_STALE_SINCE_NOV1` — findings_fold.md unchanged since 2026-11-01 16:40 PST; first judge run read an unchanged fold - is the testq fold tick running?
- `FOUNDRY_RETIRE_REVIEW_DIRTY_FILES` — Full-file code review owed (code_review_status DIRTY) for step 1-3 files: cli.py, priority.py, relentless*.py, relentless_rules/dispatcher_schedule js
- `SELFTEST_IDLE_BRINGBACK_FIX_PREEXISTING_RED` — selftest_idle_bringback is red (17 failures) and was already red at 8fc80dc7dc, before the FOUNDRY retirement
- `SELFTEST_CONDUCTOR_AUTH_FIX_PREEXISTING_RED` — selftest_conductor_authority is red (concept_tree.py his-words routes) and was red before the retirement
- `V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL` — infrastructure/state/v3_cutover/docs.patch and 'v3_cutover.py revert' would re-assert FOUNDRY ownership if run, after FOUNDRY's retirement (owner card
- `V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL` — infrastructure/state/v3_cutover/docs.patch and 'v3_cutover.py revert' would re-assert FOUNDRY ownership if run, after FOUNDRY's retirement (owner card
- `ARTPIPED_CODEX_LATCH_RETRY_ONE_BLIP_SINKS` — artpiped: a transient sandbox-read failure latches codex off for the whole run
- `ARTPIPED_CODEX_LATCH_RETRY_ONE_BLIP_SINKS` — artpiped: a transient sandbox-read failure latches codex off for the whole run
- `BRIDGE_STRANDING_DIAGNOSE_SEVEN_MORE_DRIVERS` — 7 SteveDesktop testq jobs 10-27..10-31 stranded an UNKNOWN-outcome mutating call from a live driver (non-drawbridge chains): pawn_need x4 (c14359, 1ce
- `DRAWBRIDGE_PROOF_DIAGNOSE_RESULT_WANDERS_OFF` — drawbridge_proof ran in testq J20261027T083004Z-554c07 and J20261101T083223Z-8cf7fd (after the CPU18 mask) but its 14 driver rows read UNMEASURED 'no 
- `FOUNDRY_UNITS_MIGRATE_GHOST_STILL_ON_SHIFT` — rm-codebase-health.service and rm-mirror.service still run from the retired /home/mandrake/rm/foundry clone (HEAD 95f7eaf9a9, 2026-11-02 11:37); fixes
- `FOUNDRY_UNITS_MIGRATE_GHOST_STILL_ON_SHIFT` — rm-codebase-health.service and rm-mirror.service still run from the retired /home/mandrake/rm/foundry clone (HEAD 95f7eaf9a9, 2026-11-02 11:37); fixes
- `OPS_ROLE_SHRINK_RUN_COST` — Operations alarm runs repeatedly exceed the 450k weighted-token run budget (e.g. rm-role-operations-1793686300: 486k weighted, 2.86M raw, 2026-11-03 0
- `GSS_FRAME_GARBAGE_SHRINK_HALF_MEG_LEFT` — MOD: with the snapshot world pooled (d4b91bc62e), CordBuilder.Build itself still allocates a mean 452 KB and up to 1.4 MB per AsyncLay frame at 8 latt
- `BRIDGE_CLIENT_HARDEN_FOUR_ROUGH_EDGES` — rimbridge_client.py full-file GPT review (job consult-20261102-223828-1349121) found 4 open defects: (1) a failed INDETERMINATE marker write is swallo
- `ATMOSBASE_COST_MEASURE_ELEVEN_TIMES_THE_BAR` — AtmosphericBase C1.cost FAILs live: 1.14-1.15 ms per Evaluate at 16 fixtures against the PROVISIONAL 0.100 ms bar (proof_atmosphere.py, rm_proof_atmos
- `ATMOSBASE_COST_MEASURE_ELEVEN_TIMES_THE_BAR` — AtmosphericBase C1.cost FAILs live: 1.14-1.15 ms per Evaluate at 16 fixtures against the PROVISIONAL 0.100 ms bar (proof_atmosphere.py, rm_proof_atmos
- `LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO` — Log auto-open suppressor installs only on the first jawa/ call, so plain play still pops the error log
- `OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED` — Strip player buildability from Rimefeller oil works and VHGE pump; remove VHGE's infinite starting pocket (F4: found, never built)
- `STRUCTURE_TILES_POPULATE_HOUSES_NO_ADDRESS` — Place the 14 §8 archetype TileMutators (RSW_*/RUT_* responders) on Ash'karr tiles: choose which tile gets which, then write it to the world
- `RELENTLESS_WATCH_SELFTEST_FIX_FIXTURE_GAPS` — Red on main 381e934a3a: selftest_relentless_watch 12 FAIL and selftest_ops_ranges relentless.blind FAIL because their fixtures lay no books clone (.gi
- `RELENTLESS_WATCH_SELFTEST_FIX_FIXTURE_GAPS` — Red on main 381e934a3a: selftest_relentless_watch 12 FAIL and selftest_ops_ranges relentless.blind FAIL because their fixtures lay no books clone (.gi
- `ALARM_CENSUS_EXTEND_BUILT_NAMES_SLIP_PAST` — alarm_census misses kinds built at runtime: queues.<name>.* (ops_watch) and relentless_attention_<key> both reached an unrouted incident with selftest
- `VANILLA_BEAST_LEAKS_EXCISE_ESCAPEES_AT_LARGE` — Vanilla beasts still spawn BY NAME after their CP ThingDef cut: VEE TileMutatorDefs VEE_DomesticatedEscapees (Chicken, Cow) and VEE_Megafauna (Wolf_Gr
- `L1_DONOR_SELFTEST_FIX_SARLACC_GONE_MISSING` — selftest_l1_donor_off_round.py fails 'donor rename names read for the save row' (man['donorNames']['old'] lacks sw_Sarlacc) on 1dbab17; unrelated to M
- `PHEROMONE_GENES_BUILD_SMELLS_LIKE_PROGRESS` — Zeltron and Falleen pheromones still ride on AptitudeStrong_Social; canon (zeltron/description.md: 'capable of producing powerful pheromones') says a 
- `PHEROMONE_GENES_BUILD_SMELLS_LIKE_PROGRESS` — Zeltron and Falleen pheromones still ride on AptitudeStrong_Social; canon (zeltron/description.md: 'capable of producing powerful pheromones') says a 
- `MODLIST_ORDER_FIX_LOADAFTER_WAS_A_SUGGESTION` — infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml loads mandrake.rut.patches (index 294) before mandrake.rsw.swbestiary (314), although UtinniP
- `RACES_GENERATOR_VET_SIX_GPT_HUNCHES` — gen_races_mod.py full-file GPT review (job consult-20261103-000029-1810094) raised six findings on pre-existing behaviour: --check skips verify and as
- `FAUNANORM_SETTINGS_WIRE_TWO_SWITCHES` — Mod Settings for the fauna normalization patches in UtinniPatches: an on/off for FaunaNorm_Law3_Damage.xml (whole-roster damage band) and FaunaNorm_La
- `SETTINGS_SCREENS_FIX_FIVE_OUTGREW_GROUPS` — selftest_settings_screens RED on 5 mods: WreckedMachines/UtinniPatches/WasteRun/DivingInteraction one more group than expected; StarWarsRaces abednedo
- `ARTIST_BIOME_INSPIRATION_BUILD_RESTLESS_MUSE` — Build RimMandrake/ArtistMuse (mandrake.rimmandrake.artistmuse): restless artist muse biome, Fixed mode in settings, per design/RimMandrake/artist_biom
- `LIVE_MODLIST_ENFORCE_BEFORE_SLOT` — Class fix: 6/28 live runs since 05:40Z wasted on mods absent from the game (HORRORS_RAIDING_FACTION_1 x3 'UtinniPatches not enabled in ModsConfig'; GR

## Commits

```
699d56e979 conversations: catch-up 28 record(s)
59b9279036 ledger: file LIVE_MODLIST_ENFORCE_BEFORE_SLOT
2c655e248c ledger: relentless supervisor
52661a1505 ARTIST_BIOME_INSPIRATION_MOD_1: muse design ruled (restless default, fixed as mode), build item filed
45efe18896 RIVER_SITE_REBUILD_FOR_FOURTEEN_MODS: tier gate turns a wrong-game live run into UNMEASURED, not FAIL
b69ff18b84 EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: lesson - a roster top is void on a registry-Exempt plant
39c9bf5ab5 MASS_VALIDATION_LADDER_1: A1 criterion drops the refusal sentence that tripped the live gate's flight words
07615c9d30 BIOME_WORLD_SWITCH_WAVE_1: record the offline proof; review marks for the checker
56d72ecfbf BIOME_WORLD_SWITCH_WAVE_1: offline donor-tile check on the canonical save, selftest, live proofs A2/A3
bd2eb68e31 ledger: relentless supervisor
c3369e96d6 EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: selftest pins the registry's Exempt rule in C# and the driver's result_path call site
79a3d0c7df EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: selftest follows inherited extensions/sizes and pins each top once (gpt review)
2796d3f1ae EGROWTH_TINDER_HAY_PROVE_COMES_UP_EMPTY: ScorchFruit row fireAdapted so the registry stops exempting the Tinder donor
94402346e5 ledger: relentless supervisor
f21d4f3e32 FEVERWOOD_ANT_HIVE_DUNGEON_1: settings-screens selftest catches up with 5 later groups; multi-line Group() parsed
3acbc3478c ledger: relentless supervisor
c3212dd73e FAUNA_TOLERANCE_NORMALIZATION_1: code-review clean marks + ledger
06e6d6d268 FAUNA_TOLERANCE_NORMALIZATION_1: Laws 3/5/6 over the whole roster — generator, manifest, 3 UtinniPatches patches
bf04d0857e ledger: relentless supervisor
b5efc00aa7 PLAYER_START_SITE_1: clean marks for the pinned selftest and live proof (GPT consult-20261103-000332-1821743)
... 1049 more: git log --oneline 0ea101167c..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-03T08:23:47Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/code_review/BENCH.jsonl   Relentless/publisher ledger churn, not this window's work
 M infrastructure/state/ledger/events/BENCH.jsonl   Relentless/publisher ledger churn, not this window's work
?? cards.json   Relentless/publisher ledger churn, not this window's work
```

