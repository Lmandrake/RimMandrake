# BENCH_REBOOT_HANDOFF_202610261756 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610260731`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 Owner order (2026-10-26 ~07:15, by card): burn hard before Wednesday on FlowWorks live blitz + review debt (many reviewers) + art audit across all creatures, **6 helpers at once**, and his explicit condition *"you need a strategy to keep git healthy"*. The strategy that worked all day: reviewers/builders each work in a PRIVATE scratch clone (`scratch_clone.py clone … --checkout --fetch`, `git pull --rebase` before `./publish`); exactly ONE builder per DLL project at a time (others file C# items); on a DLL/.srchash rebase conflict take origin's and rebuild, never hand-merge; shard files (ledger, code_review) committed whole and append-only vs origin — an uncommitted foreign line left mid-file makes the next whole-file commit fail ledger_lint NOT_APPEND and ./publish retries forever (filed: lessons 20261026T110108Z); builders must NOT mark their own files CLEAN (filed: lessons 20261026T171949Z). Applies until he changes it.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Art sheets waiting for his look (all prereviewed): 7-set whole redraws `D:\Luke\dev\RimMandrake\Transient\biome_ffar\art_eval_shadow_wholeset_20261026_s1r3_sheet_2026-10-26.html` (6 installed; CanopySwinger north still reads top-down; Starmaw streamers hang down) + CoolantEel north on `art_eval_shadow_facingfix_20261026_r2_sheet_2026-10-26.html` (kept art replaced under his "show me after" card). Reverts: `D:\ClaudeWork\rimmandrake\facing_backlog_20261026\{wholeset,batch,redraw}\revert\REVERT_ARGV.txt`.
- Audit batch installed 16 creature redraws today (no sheet built yet — owed, see pointers).
- Hose reel sheet `D:\Luke\dev\RimMandrake\Transient\biome_ffar\hose_reel_firehose_on_the_drum_sheet_2026-10-24.html` still unruled (blue vs red frame).
- Phone brief A7: he has not yet opened http://archmagi-wsl:8791/ (RIMPULSE_BRIEF_BUILD_MORNING_PAPER_PHONE).
- ColdStorage is now in his ACTIVE mod list (FULL.LATEST, 321 mods) — new mod, loads with "patched 10, missing 0", untested live. RimFridge still present (drop after our units ship, his card).
- Delegated calls today: digest `D:\Luke\dev\RimMandrake\Transient\delegated_digest_2026-10-26.md` (later calls: specimen tank releases occupant on destroy; sapper ladders 0% = none; tar vat heats only while worked; stasis grade ladder 0.8/0.25/0).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FACING_SETS_REDRAW_WHOLE_SET_ESCALATED` — 6 of 7 installed; Muttavaq escalated (N/S shape mismatch after 3 rounds); NEXT: show the owner the s1r3 sheet and ask whether to redraw Muttavaq from a new canon brief or keep it.
- `JAWABENCH_TPSARCHIVE_FIX_SKIPPED_AFTER_FAULT` — fixed 9ad1d55242, deployed, one clean start seen; NEXT: submit 20 cold starts on SteveDesktop and close if no new Crash_* folder.
- `JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT` — fixed 9303ac5721, deployed with the above; NEXT: close together with the 20-cold-start proof.
- `HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP` — live round 5 FAIL: T2 frame max 5920 ms, DrawAll 5917 ms, LayFromOn mean 1171 ms / max 6922 ms; GC down to 9/29 s; timed phase PASS (100/100 rigs, 10.7 ms max); evidence D:\ClaudeWork\rimmandrake\live_round5_20261026\; NEXT: profile why DrawAll still waits ~6 s on lays (a main-thread wait/apply path or synchronous EnsureLay fallback) and cut LayFromOn cost, then re-run T2+T3.
- `GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG` — sliced builds b81e7543d4 + 8474ca747f deployed, not measured live; NEXT: run the item's live recipe (maxSliceMs<20, far dig → farSkips+1).
- `COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE` — engine, coolers, seals, stasis built; engine+coolers deployed, seals/stasis not; NEXT: deploy ColdStorage+Cuisine+TheSump from HEAD and run every step on the item.
- `FACING_AUDIT_BUILD_REDRAW_BATCH` — 16 installed; stopped mid group 1c_SWBestiary (run audit_20261026_c1r1); NEXT: build shadow sheets for runs audit_20261026_b1r1/b1r2/c1r1, then continue the plan at D:\ClaudeWork\rimmandrake\facing_backlog_20261026\redraw_batch_plan.md.
- `PIT_SUPERDEEP_COLLAPSE_1` — walk restaged 1ab634fd6d; NEXT: re-run stations S2,S5,S7,S8,S9,S10 live.
- `GSS_PROOF_DRIVERS_FIX_FALSE_PASS` — rows 9.1–9.5, 9.7, 9.8 open; NEXT: fix them per gptfw_progress.md with selftests.
- `REVIEW_MAP_FILL_FIVE_UNSTATIONED_DEFS` — selftest_review_map red at HEAD; NEXT: add stations for the 5 defs and make the selftest green.
- `COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS` — not started; NEXT: build it in a scratch clone (one ColdStorage builder at a time).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- An uncommitted shard line left mid-file blocks every later publish via ledger_lint NOT_APPEND. (filed: lessons 20261026T110108Z)
- Builders self-mark their own files CLEAN; reviewers then found real bugs in them. (filed: lessons 20261026T171949Z)
- A per-day job-count / budget limit can silently skip drivers (thirst_live always SKIPPED_BUDGET) — size jobs from declared driver timeouts. (see: TESTQ_SIZING_FIX_DRIVER_BUDGET_FROM_PLAN)
- Proof scenes that restore state only in Verdict leak it on failure; proof_restore_check.py now guards. (filed: lessons 20261026T161651Z)
- `./publish` rebases: close items only after publish, citing the published sha. (filed: lessons 20261026T094120Z)
- A decompile of RimWorld 1.6 exists at D:\ClaudeWork\rimmandrake\decomp\rw16\all\ — check vanilla calls there. (see: review_debt_20261026 progress files)

## Closed since the last handoff (137)

- `LADDER_PRISON_FIX_COLONIST_STAYS_HELD` — 89a9a69600
- `POOL_PIT_FIX_DROWNING_CENSUS_EMPTY` — 89a9a69600
- `NATURAL_SLIME_FIX_WALKER_NEVER_SLIPS` — 89a9a69600
- `TESTQ_SWEEP_WIRE_FLOWWORKS_DRIVERS` — 1c3f90d62d
- `FLOWWORKS_SELFTESTS_FIX_TMPDIR_LEAKS` — 27f50667c8
- `VALIDATE_PATCH_DESCENDANT_FIX_FALSE_ZERO` — ee3a515e5f
- `TESTQ_INGEST_FIX_ONE_ITEM_MANY_ROWS` — c6696800ed
- `TESTQ_FILL_CAP_SCALE_AND_SKIP_DRY` — 86b0475881
- `STEVEWORKER_HARDEN_THREE_LOOSE_BOLTS` — 3dc1e6828b
- `STEVEWORKER_UNSTICK_DIRTY_CLONE_REFUSES_SYNC` — 0fac8aa4c4
- `STEVEWORKER_HARDEN_OLD_PIN_RUNS_OLD_CODE` — 0fac8aa4c4
- `MISSION_FIXTURE_FIX_RESEARCH_WINDOW_BLINDS` — f8e7b364d1
- `LIQUID_TERRAINS_FIX_DRUNK_AS_FRESHWATER` — 25f2a98e95
- `RIVER_CHAINS_WIRE_SWEEP_TO_RIVER_SITE` — e7ea84ae17
- `GATESELFTEST_FIX_PIN_MINIMAL_LIST` — 6340b6b3474acc538a0c039183ea958fae40920c
- `PIT_CAPTURE_FIX_HOSTILE_NOT_PRISONER` — 89a9a69600
- `PIT_CAPTURE_FIX_FIXTURE_FIGHT_STOPS_CHAINS` — 948ae1b7fc
- `HOSE_PORT_SELFTEST_FIX_P9_CREDIT_COUNT` — efa77807b7
- `LEVEL_PERF_PROOF_FIX_LAYS_OUTRUN_BUDGET` — 5795589380
- `DRAWBRIDGE_ART_FIX_STALE_CABLE_MEASURE` — 829e1d903c
- `BLACKSTAR_SAPPERS_RESTORE_BREACH_KIND` — e61396125c
- `BRIDGETOOLS_WORKGIVER_PROBE_ANIMAL_NRE` — 32f201f1bf
- `ARCHITECT_VISIBLE_FIX_READS_ALWAYS_TRUE` — f5d0dad43e
- `TESTQ_DISPATCH_PUSH_ENFORCE_LINT` — 03a71088f831
- `RIVERSITE_FIX_RETILE_NONE_CRASH` — c7f7849afe
- `TESTQ_JOB_PLAN_WIRE_PREVIEW` — 8f39225abd
- `LINES_PROOF_FIX_POLE_SPAN_SITE` — 075dec75a7
- `V2_FILLIN_SCENE_STAGE_FILL_MATERIAL` — 075dec75a7
- `THIRST_FIX_SALT_DRUNK_ROUTINELY` — 075dec75a7
- `THIRST_FIX_DESPERATE_SKIPS_BOTTLE` — 075dec75a7
- `THIRST_FIX_AWKWARD_ACCESS_ROW_FAILS` — 075dec75a7
- `TOGGLE_LADDER_FIX_REQUIRED_PAWN_ESCAPES_PIT` — 075dec75a7
- `WASTES_BRINE_FIX_RUT_TERRAINS_DRUNK_FRESH` — 7acc759d82b7
- `MIRE_FUZZ_FIX_FREE_STRUGGLE_BLIND` — 7acc759d82b7
- `WARCASKET_FUZZ_FIX_SWIMMER_COMMENT_WRONG` — 7acc759d82b7
- `STILLSAND_FUZZ_FIX_RUNOUT_TICKS_MISSTATED` — 7acc759d82b7
- `TESTQ_ARCHMAGI_FIX_OWNER_MODLIST_SWAP` — eddc7f3d3787
- `RIMPULSE_LOOKS_BUILD_PACKET_IN_WIDGET` — e4374511305d
- `ICEDIG_SELFTEST_FIX_STALE_MOD_GATE` — 8c8b2ac78032
- `METEORITE_ADAPTER_PROVE_LIVE_CHAIN` — e99a6c8566
- `HOSE_SHADOW_FIX_STALE_AFTER_RELAY` — 760592195a
- `HOSE_SHADOW_FIX_RETRACTING_STRAND_STALE` — 760592195a
- `HOSE_SHADOW_FIX_CARRIED_STRAND_STALE` — 300816d5f4
- `HOSE_FRAME_SHRINK_PER_FRAME_GARBAGE` — 525f34a3c4b4
- `MACHINERY_LOOK_FIX_DECK_REPAINT_ON_SWITCH` — 6de559bc87
- `WEIR_SELFTEST_FIX_STALE_DEPOSIT_ANCHOR` — 082fae61e9
- `STATIC_STATE_FIX_RELOAD_TICK_MEMOS` — 082fae61e9
- `FAUNA_SPEC_SWIMMER_FIX_WALKER_MODULE` — 7743471e29
- `ARTPIPE_JOBS_WIRE_BODY_PLAN_CLAUSE` — 9b4ed7a53b
- `TESTQ_FIX_COMPOSE_ROUTE_MOD_WITH` — 26e691ce7271
- `FLOWWORKS_V2_FIX_PIT_ROWS_RESCUE_LADDER` — e437451130
- `ARTPIPED_STATUS_FIX_PHANTOM_INFLIGHT` — d870e27cf3
- `CODEX_SEED_FIX_STALE_RUNNER_BUILD` — f7a33d06ee
- `CODEXSEED_FIX_FALSE_UAC_HINT` — b8c65ab2a9
- `STEVE_RIG_FIX_OUTOFBAND_DRIVER_MARKER` — e13c4cc9df
- `HOSE_LOOK_FIX_RESET_SKIPS_REPAINT` — edc9b8335227
- `MODCHECK_DRIVERS_FIX_BUDGET_KILL_MIDCALL` — 06c8d1e10d3304ed23bfd4beb0e6da877e99122a
- `TESTQ_SIZING_FIX_DRIVER_BUDGET_FROM_PLAN` — 4a63a952ef98
- `STEVEWORKER_FIX_MARKER_BOUNCE_EVERY_JOB` — a961a0a251
- `FAUNASPEC_FIX_FLIGHT_FRAMES_IGNORE_PREFIX` — 996f892c7e
- `MODCHECK_DRIVERS_HARDEN_OWN_TIMEOUT_MIDCALL` — 21866d895a2c
- `TESTQ_FIX_CANARY_PAUSE_IDLES_LANE` — 9c156d42aa31ed90197427c18c826719503b2f7d
- `TESTQ_SWEEP_FIX_DRIVERS_OVER_CAP` — c69b2fc1e3
- `ARTEVAL_RUNNER_FIX_FILES_UNSPECED_KEPT` — d4eb6f0491
- `SELFTEST_ARTPIPE_FIX_UNPINNED_NETEXE_ENVS` — c6f662476c
- `FILLQUEUE_ENFORCE_ELIGIBILITY_GATE` — ea640a7247
- `HOSE_SHADOW_VERIFY_RELAY_AND_WIND_LIVE` — 760592195a
- `ARTGATE_FIX_UNBOUND_SLOT_FILINGS` — ea640a7247
- `ELIGIBILITY_GATE_WIDEN_TO_TERRAIN_WEATHER` — 3ddc13cb5b
- `CHILLFIREGATE_FIX_STALE_IDENTITY_COMMENT` — 402cce50a2
- `RIMBRIDGE_DEADLINE_FIX_NAN_FAILS_OPEN` — 5acc7c9c33
- `MODCHECK_REUSE_TEST_FIX_VACUOUS_CANARY` — 5acc7c9c33
- `FILLQUEUE_GATE_FIX_MIXED_FACING_EXEMPT` — e22d1a7ed0
- `ARTEVAL_RUNNER_FIX_TEST_RESUMES_PROD_RUN` — db86c8e699fe
- `EXTPROOF_FILLIN_FIX_STALE_BUDGET_DOC` — 4f55957f6b78
- `FILLQUEUE_OWNERRULING_FIX_ANY_RULING_PASSES` — 9906e72484
- `MODCHECK_VALIDATE_FIX_OWNER_WORDS_DROPPED` — 4946dcddef
- `HOSE_ROUTE_FIX_THREAD_BUDGET` — a188c6f43f
- `HOSE_LAY_FIX_STALE_EPOCH` — a188c6f43f
- `HOSE_LAY_FIX_GLOBAL_CAP` — a188c6f43f
- `HOSE_LAY_FIX_COUNTER_ORDER` — ef18f77fc5
- `HOSE_LAY_TEST_FIX_VACUOUS_EPOCH_SCAN` — e9f80eff59
- `BRIDGE_ART_REDRAW_CABINETS_GROW_SADDLES` — 97b09eddea
- `REACH_MAP_BUILD_WALLS_AND_DEPTH_AGREE` — b5e399067a
- `HUMANREVIEW_FIX_UNMEASURED_FRESHNESS_PROVES` — ede26bdb6e
- `RIVERSITE_FIX_UNANSWERED_CALL_CRASHES` — 0c61353fac
- `COLD_STORAGE_ENGINE_BUILD_CLIMATE_COMP` — 09a5462468
- `COLDSTORAGE_REGISTRY_FIX_STALE_AFTER_LOAD` — 2727a45c4a
- `COLDSTORAGE_CLIMATE_FIX_TEXTURE_CCTOR` — 2727a45c4a
- `COLDSTORAGE_LWM_FIX_COMPS_NOT_EXTENSION` — 2727a45c4a
- `FERRYROPE_FIX_VANISHES_OFFSCREEN_OWNER` — 605184de03
- `COUPLER_REDRAW_FIX_STALE_ACROSS_SECTIONS` — 605184de03
- `LADDERPARITY_FIX_TAKE_WORK_SAPPER_ZERO` — 605184de03
- `RIVERPROOFWORKS_FIX_STALE_CALLER_AND_LEAKS` — 605184de03
- `RIVERCURRENT_FIX_STALE_DOC_AND_BARE_ENGLISH` — 605184de03
- `PUMPPREVIEW_PRUNE_STALE_PORT_DRAW` — 605184de03
- `FLOWWORKS_KEYS_PRUNE_DEAD_DRILL_STRINGS` — 605184de03
- `BANKWORKS_PRUNE_ORPHAN_PLACEHOLDER_ART` — 605184de03
- `RIVERDRIFT_DOC_FIX_CLAIMS_NOTHING_READS` — 605184de03
- `SPIKES_DOC_FIX_STALE_D4_ONLY_HEADER` — 605184de03
- `SEKKULAATHTANK_DECIDE_RELEASE_ON_DESTROY` — e696f6d185
- `CLIMBLIMIT_DOC_FIX_SUMMARY_ON_WRONG_MEMBER` — 605184de03
- `SUSPENSIONMATH_DOC_FIX_SLICE_SAYS_ROWS` — 605184de03
- `RIVERMATH_DOC_FIX_STAKE_ORDER_GRACE` — 605184de03
- `RAIDERTRENCH_DOC_FIX_STALE_OWN_FACTION_RULE` — 605184de03
- `FLOWKERNEL_DOC_FIX_STALE_SURFACE_RANGE` — 605184de03
- `FLOWWORKSMOD_DOC_FIX_STALE_PHASE_NOTES` — 605184de03
- `COLDSTORAGE_SEALED_READOUT_FIX_GATE` — c5b82ed617
- `COLDSTORAGE_STASIS_WIRE_GRADE_FACTOR` — c5b82ed617
- `COLDSTORAGE_DECAY_READOUT_FIX_UNDER_STASIS` — c5b82ed617
- `COLDSTORAGE_MINIFIED_FIX_STALE_TEMP` — c5b82ed617
- `ORPHANART_FIX_MISSED_READERS_NO_COPY` — df07ce83d6
- `PITWALK_FIX_SHOT_RELPATH_ACROSS_MOUNTS` — 8ab4647364
- `PITWALK_FIX_FIVE_ROWS_NEVER_MEASURE` — 8ab4647364
- `PIT_EXPOSURE_FIX_NO_HEDIFF_OPEN_FLOOR` — 8ab4647364
- `PIT_FLOOD_FIX_NEAR_BRIM_NO_EXIT` — 8ab4647364
- `COLD_STORAGE_COOLERS_BUILD_RSW_LADDER` — 46cdb52ab7
- `SETTINGS_SCOPE_LINE_CORRECT_NEXT_PULSE_LIE` — 878bd55620
- `COLDSTORAGE_WALL_LIGHT_FIX_RESYNC` — bac56b6b50
- `COLDSTORAGE_WALL_PRISON_FIX_HEMOGEN` — bac56b6b50
- `SEAT_SYNC_HARDEN_LITERAL_PATHSPECS` — 9ea0915ca7
- `CONVERSATIONS_LAND_FIX_STALE_TRAILER` — 68d9a4df18
- `TPS_VERDICT_FIX_WINDOW_LABEL` — 074895cc0f
- `PLACEHOLDER_GENS_PRUNE_REAL_ART` — b6e3cd89bd
- `TRANSIENT_PIN_FIX_STALE_TRAILER` — 432f02daf1
- `HOSE_CENSUS_FIX_RELAYS_IN_PROBE` — fa833277f811
- `GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS` — 5dae2afe31
- `COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE` — dff5f0da7b
- `COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT` — dff5f0da7b
- `FW_PROOF_DRIVERS_FIX_EARLY_FALSE_PASS` — ea8d2a6fc9
- `COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS` — 367f0e9c2627
- `PIPE_ARM_FIX_STALE_BESIDE_NEW_TANK` — 1bce1ead7a11
- `RIVERPROBE_FIX_FOUR_UNGUARDED_SPAWNS` — 1bce1ead7a11
- `LADDERINSPECT_FIX_WALL_LEAN_SAYS_NOWHERE` — 1bce1ead7a11
- `WEIRCHECKS_FIX_REGEX_READS_NEXT_DEF` — 1bce1ead7a11
- `DETACHEDBED_HARDEN_REATTACH_NO_WATER` — 1bce1ead7a11
- `FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS` — 861069cb4a

## Filed and still open (42) — the next seat's queue

- `THIRST_FIX_SLIME_ROWS_NEED_BIOMES_TIER` — SITE (probable): thirst/T15_slime_effects FAIL (job J20261026T060806Z-09152f): red pawn drank RM_SlimeRedShallow with no hediff/memory; red/green/whit
- `PROPANE_PIPES_DECIDE_FLOWWORKS_LANE` — Lane check: RUT_PipeSegment (PropaneLakeMechanics, pipes) arguably sits in BENCH's FlowWorks lane. FOUNDRY changed it in 2965619d82 (tickerType Normal
- `TILEMAP_GENERATE_FIX_SETTLEMENT_NRE_LOOP` — jawa/world_tile_map_generate tile=96545 (RUT_TheRot faction Settlement, mapGenerator Base_Faction) leaves the world in an NRE loop: every world tick S
- `RIVER_STEAM_BUILD_PYRELANDS_SWEEP_SITE` — toggle_river_steam ON/OFF half needs a Pyrelands map the sweep has no driver for (Pyrelands/northstar_site.py builds a scratch world: worldgen-ban que
- `GAME_STATICS_FIX_SEVEN_UNREVIEWED` — selftest_static_game_state 7/101 FAIL: 7 static per-game fields unreviewed (RM_PipeStraightVariantsDraw.cs:19 mats, RM_DrawbridgeArt.cs:249 leafMeshes
- `AGARILUX_PRINT_FIX_NRE_ON_RELOAD` — Plant.Print NRE 'Exception printing RM_GiantAgarilux<id> at (x,0,z)' x8 after loading BENCH_leaf_scenes_20261026 on the full list (stack: Plant.Print 
- `FILLIN_PROOF_FIX_ORDER_NEVER_FILLS` — fill_in proof orders a bare fill job that ends at once; pit reads D=7 not 1, never fills
- `JAWABENCH_TPSARCHIVE_FIX_SKIPPED_AFTER_FAULT` — JawaBenchTpsSampler.cs:458-465 RootFinalizer: PumpArchive runs only after the __exception/RuntimeError early returns, so a sampler fault before 10 s o
- `JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT` — 6010f2a3d6 deferred only the Player-prev archive; install still starts background JIT while the ctor goes on Harmony-patching (JawaBenchTpsSampler.cs:
- `FILLIN_PROOF_FIX_BYSTANDER_DOWNED_MIDWAIT` — toggle_fill_in fill_in_on UNMEASURED (J20261026T090334Z-0c5943, 473fcecf31): the order now runs, but a bystander colonist Hansol (46068, not the fixtu
- `FACING_SETS_REDRAW_WHOLE_SET_ESCALATED` — 7 facing sets escalated after 3 art-eval rounds: Dovvik (redraw outline darker), CanopySwinger/Thrummel/BrineBattery/FireWasp-dessicated (norths/east 
- `SHADOW_KEPT_SWAP_ENFORCE_FLAG_ON_ACCEPT` — policy.replaces_kept is true only for REGEN, so an ACCEPTed redraw of owner-kept art (RM_CoolantEel north, facingfix_20261026_r2, installed by card) s
- `HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW` — Hose re-lays (LayFrom path search) run synchronously in DrawAll/EnsureLay: one maxLength change froze one frame 90.5 s (150 re-lays), the proof's 80->
- `SPECIES_HEADS_AUDIT_PROVENANCE_BEFORE_REDRAW` — Cosmetic species-head art (Togruta heads + montrals, Twi'lek, Duros, Bothan, Gungan, Herglic, Dathomirian) cannot be queued: fill_queue dry-run 2026-1
- `TAUNG_NAMES_DESIGN_WITHOUT_CANON_POOL` — RSW_RimMandrakeTaung has no nameMaker: Wookieepedia Category:Taung (fetched 2026-10-26) holds only epithets and titles, no personal names, so no canon
- `FACING_AUDIT_BUILD_REDRAW_BATCH` — Redraw the 169 creature facing sets the 2026-10-26 audit failed (a14 b85 c58 d12); per-set list in D:\ClaudeWork\rimmandrake\facing_backlog_20261026\a
- `EVICTIONGEN_PRUNE_CORPSE_ROWS_NEVER_MATCH` — BiomeCastEvictions_WildBiomes.xml: 1267 of 2018 ops target Corpse_* ThingDefs, which are code-implied (ThingDefGenerator_Corpses via PlayDataLoader:17
- `HOSE_LAY_FIX_GC_STORM_FROM_WORKER` — Worker hose lays (HoseLayQueue.LayFromOn, mean 650-736 ms, max 7.3 s on the 325 map) allocate enough to force a full Boehm GC about every 1.2 s on a 3
- `HOSESNAP_FIX_HEADING_AND_RAMP_SCALE` — HoseClothoid.Snap reports Feasible with a heading error up to SnapTurn (50x EndTol), and rescales the ramp bound as dk/sc where the stretched curve al
- `GSS_PLAN_FIX_SECOND_PER_FULL_BUILD` — GSS build that plans cords (not reused) now takes ~1 s on the 325-map lattice (E=248): lattice placed 1026 ms, 84 lamps placed 1009 ms, bEdges 997 ms 
- `COLD_STORAGE_BUILD_OWN_LINE_DROP_RIMFRIDGE` — Own Star Wars cold-storage line replacing RimFridge: chill cooling units (sizes x tech), Rakatan full-stasis chambers (ship unlock + vault loot), carb
- `COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS` — Step 5 (design/RimStarWars/cold_storage_line_2026-10-26.md §4.3): RSW_CarbonFreezingPress 2x2 300W (canon miniature carbon-freezing chamber), RSW_Carb
- `COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES` — Step 7 (design/RimStarWars/cold_storage_line_2026-10-26.md §5): Cuisine dishes that REQUIRE a method: RSW_CarboniteNCreamPie (blast-chill), RSW_Pickle
- `COLD_STORAGE_ART_BUILD_SPRITE_BATCH` — Step 8 (design/RimStarWars/cold_storage_line_2026-10-26.md §7): ~14 building sprites + 3 stasis grade variants + ~33 item icons + VCE ration-sealer re
- `COLD_STORAGE_PROOF_VERIFY_ROT_RATES_LIVE` — Step 9 (design/RimStarWars/cold_storage_line_2026-10-26.md §9.9): live proof on 13-mod minimal list + Cuisine + TheSump: measured rot per mode (chill/
- `RIMFRIDGE_DROP_FIX_INBOUND_REFS` — Step 10 (design/RimStarWars/cold_storage_line_2026-10-26.md §1/§9.10): after step 9 and owner Q1 (doc §10), RimFridge leaves the active list (owner-fa
- `TELEMETRY_HARDEN_FIX_FOUR_EDGE_CASES` — Telemetry edge cases from review debt part 3: wsl_export ledger_seen set grows without bound; art/game_art.py precommit reads worktree not index; tele
- `TELEMETRY_FAKE_DEPLOYS_EXCISE_NOT_REWRITE` — Telemetry: 159 fake deploy rows (ModA x143, ModNew x16; 2026-10-11T21:26..10-26T10:05Z) from selftest dummy mods sit in inbox/changes, raw/*.jsonl.gz 
- `COLD_STORAGE_LADDER_ART_JUDGE_SHEET` — Judge the 13 artpipe jobs for the cold-storage ladder (RM_EvaporativeCrock single; RSW_CoolingSupplyUnit/_Wall/Chamber/CryoUnit south+east+north; list
- `COLD_STORAGE_CHAMBER_BUILD_DRINKS_CHILLER` — The design's drinks-chiller variant of RSW_CoolingChamber (a label/filter variant for beverages) was not built in LADDER (46cdb52ab7); build it or dro
- `COLD_STORAGE_RSW_RESEARCH_VERIFY_LAYOUT` — RSW_CoolingUnits (view 5.00,5.60) and RSW_CryoStorage (16.00,5.60) were placed without checking the research tab on the full list; confirm in game the
- `HOSE_SELFTESTS_FIX_MISPLACED_DOC_NAMES` — FlowWorks SelfTest cosmetics from review 2026-10-26: HoseCarryChecks.cs ~233 Row6Legacy's <summary> now sits above CarryBranchDropsStrand (two summari
- `ACCEPT_LOOKS_DECIDE_REJECTS_STILL_STAND` — decisions_v2 --accept-looks picks a render the owner had x-rejected or assigned not_needed
- `FLOWWORKS_PROOF_POKES_RESTORE_PRIOR` — FlowWorks proofs: 55 setting/def pokes not restored to the prior value on a throw (7 C#, 48 py; proof_restore_check.py)
- `SEA_DIVE_PROOF_RESTORE_PRIOR` — prove_sea_dive_floor.py:85 sets mod settings with no finally restoring the prior values
- `HOSE_PROOFS_FIX_STALE_LAYOK_AFTER_PEEK` — Since fa833277f8 the hose census reads the cached lay (r.lay) and never lays. Proof rows that act and then read census layOk at once (validation_hose.
- `KYBER_GATE_DEPLOY_AMID_FOREIGN_DRIFT` — Deploy the def-keyed kyber gate (UtinniPatches RUT_LanternDeepGateKyber.xml + RUT_LanternDeepKyberScatter.xml MayRequireAnyOf) and Armoury's 3 Absorbe
- `FW_PROOF_TOOLS_HARDEN_READ_GAPS` — Proof bridge reads lack fields the proofs need (GPT 4.5+7.12 excavation liquid/dL, 6.2 pulse dL, 6.4 InFloorBand read, 7.1 proof_hose DLL stamp, 7.11 
- `GSS_PROOF_DRIVERS_FIX_FALSE_PASS` — GSS validation false PASS and leaks (GPT 9.1-9.5, 9.7, 9.8) - file:line + fix in D:\ClaudeWork\rimmandrake\review_debt_20261026\gptfw_progress.md
- `RAKATAN_STASIS_LOOT_BUILD_HELD_PROVISIONS` — Design §4.2/§5 layer 3 leftovers: RUT_StasisHeldProvisions (chambers found still holding provisions) and chamber placement in the RUT war-lab rooms. O
- `STASIS_LOCKER_BUILD_ANCIENT_COMPLEX_LOOT` — RM_AncientStasisLocker (generic layer-1, mandrake.rm.coldstorage, 367f0e9c26) has no loot source yet: place Wrecked/Kludged lockers in vanilla ancient
- `REVIEW_MAP_FILL_FIVE_UNSTATIONED_DEFS` — selftest_review_map.py red at HEAD: RM_RaiderFetchFill, RM_LadderSteel, RM_CrushedIce, RM_IceMelter, RM_MeltCrushedIce have no numbered, labelled, den

## Commits

```
79b4fb98ae conversations: catch-up 2 record(s)
078e60209d ledger: OWNER shard
028a3eaae1 ledger: BENCH bridge release after live round 5
cb8f6b4dfe DIANOGA_FIX_YOUNGCASK_LABEL_LEFTOVER: RSW_Sekkulaath_DianogaGiant.xml now relabels RM_SekkulaathYoungCask "dianoga young-cask". The cask def (6c34f761ae) postdates the reskin (b1948944cd), so with the SW tier loaded it was the one player-facing "sekkulaath" left in the 2026-10-26 dump. Its description names nothing, so it stays as written. The brood-ransom young follows the tank swap through YoungKind/occupantKindDefName. New selftest_dianoga_reskin_coverage.py requires every top-level Fever Wood label/description containing "sekkulaath" to be the target of an op in a SW patch. It is red on the old file and green now. validate_patch (Data + workshop + Mods + live dump): 0 errors, new op 1 match.
1ee7574a69 GRAFFITIIMPERIAL_VALIDATION_FIX_LOST_REASON: GraffitiImperial validation.py _comp set upstream_reason = None after lifting a row's UNMEASURED. A later plain FAIL latches without setting a reason, so in framework_wiring (row 1 shape unreadable -> UNMEASURED, row 2 sibling unresolved -> FAIL) empire_faction_def_resolves read UNMEASURED with detail None. _comp now restores the prior reason. New selftest_graffitiimperial_unmeasured_reason.py drives the production chain through modcheck's TestContext on a fake bridge: red on the old file, green now; static PASS.
a71281e42a BRAINWORMS_VALIDATION_FIX_BORROWED_REASON: BrainWorms validation.py infection_state is stateful (row 2 reads the pawn row 1 infected), but _comp lifts row 1's UNMEASURED, so with the hediff hidden from pawn_get row 2 ran on and reported a symptom ("pawn_get hediff rows carry no severity field") instead of the cause. Row 2 now names the row above's reason when no readable infected pawn was established. _comp also restores the prior upstream_reason instead of None (a later plain FAIL latches without setting one, leaving later rows with no reason). New selftest_brainworms_unmeasured_reasons.py (modcheck TestContext, fake bridge): red 2 checks on the old file, green now; selftest_brainworms green; static PASS.
a096f60c91 GIZKA_VALIDATION_FIX_LOST_REASON_DONOR_PICK: three harness faults in GizkaStowaway validation.py. (1) _comp set upstream_reason = None after lifting a declared UNMEASURED; a later plain FAIL latches without setting a reason, so every row after it read UNMEASURED with detail None (harmony_wiring: 3 rows). It now restores the prior reason. (2) donor_patch took the first resolving kind, the donor's Gizka, but only RSW_Gizka is patched (the donor block was deleted in 3265277e01): a false FAIL on 100 whenever the donor loads. It now reads RSW_Gizka only, UNMEASURED without it. (3) static_checks still demanded the deleted donor block: STATIC FAIL on HEAD; now checks the port's single MarketValue 15 and its targets. New selftest_gizka_validation_chains.py (modcheck TestContext, fake bridge): red 3 checks on the old file, green now with an unpatched-port FAIL control; selftest_gizkastowaway green; static PASS.
2c71d47a08 ledger: close ART_SELFTESTS_FIX_LIVE_DATA_DRIFT at a69cfd0b3a; ARTPIPE_TWINS_PRUNE_FAILED_COPY blocked on new ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG (31/32 twins have no PNG; prune not applied)
e7c155da4e ledger: live round 5 hose T2 fail (5.9 s frames), levelling timed PASS links 100, cold storage load note
9a5b67555a ledger: close FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS at 861069cb4a; GSS rows note; file REVIEW_MAP_FILL_FIVE_UNSTATIONED_DEFS
7c8ee6cf54 ledger: close FlowWorks fix batch 2 (5 items at 1bce1ead7a11), note 2 skipped hose items; lesson: shared selftest dotnet lock
861069cb4a proof drivers: late false passes 7.7, 8.1, 8.2, 8.4-8.9 fixed; 7.4/7.5 paths tested (FW_PROOF_DRIVERS_FIX_LATE_FALSE_PASS)
1bce1ead7a FlowWorks C# fix batch 2: pipe arm redraw, river probe cleanup, ladder lean inspect, weir def regex, detached bed reattach
ab54278955 ledger: FACING_AUDIT_BUILD_REDRAW_BATCH stop-point note
c23f13add0 FACING_AUDIT_BUILD_REDRAW_BATCH: class d round 2 + class c round 1 (partial): 11 sets installed
679ef5a571 code review: close-out wave batch 2 (wet_costs_live CLEAN, full read)
63a9c8053f ledger: note COLD_STORAGE_CARBONFREEZE_BUILD_FOOD_PRESS not started (handoff)
bf74c8c157 ledger: close COLD_STORAGE_STASIS_BUILD_RAKATAN_CHAMBERS at 367f0e9c26; live steps; 2 follow-ups; 2 lessons
6072b7a785 code review: close-out wave batch 1 (HarmonyPatches, Seals_Bases, validation_core, thirst_fake, sweep_identity_proof, trench_crossing_live, selftest_gptfw_review_fixes CLEAN)
537392ae3c northstar drivers: four more end main() on validation_core.rows_exit (UNMEASURED exited 1, no rows exited 0)
... 685 more: git log --oneline 66cebda636..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-26T17:55:21Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? infrastructure/state/art_eval/runs/facingfix_20261026_live/kept/   BENCH art helpers 2026-10-26: kept-art revert copies, deliberately untracked (earlier runs never commit kept/)
?? infrastructure/state/art_eval/runs/facingfix_20261026_r1/kept/   BENCH art helpers 2026-10-26: kept-art revert copies, deliberately untracked (earlier runs never commit kept/)
?? infrastructure/state/art_eval/runs/facingfix_20261026_r2/kept/   BENCH art helpers 2026-10-26: kept-art revert copies, deliberately untracked (earlier runs never commit kept/)
?? infrastructure/state/art_eval/runs/wholeset_20261026_s1r2/kept/   BENCH art helpers 2026-10-26: kept-art revert copies, deliberately untracked (earlier runs never commit kept/)
```

