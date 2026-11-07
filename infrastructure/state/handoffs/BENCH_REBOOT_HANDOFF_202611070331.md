# BENCH_REBOOT_HANDOFF_202611070331 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611061923`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The owner stopped the pipeline at 18:22 PST: "Stop the pipeline immediately. This is broken. I will work with you later in person to help it. No further runs except for test runs allowed." Then he allowed the art pipeline and a Ralph loop on Graffiti. The bench clone is level with origin; copies I moved aside are in D:\ClaudeWork\backups\bench_level_20261106. Do not restart Relentless, the Dispatcher or the disabled timers until he sits down with us; a new window must not "fix" the red DISPATCHER NOT TICKING line. Undo list: `PIPELINE_RETHINK_OWNER_STOPPED_BURN`. His diagnosis, and mine: 360 items closed a day and 0 of 135 mods accepted, 1.1M tokens an item, with the agent who sees the whole picture barred from acting and the agents acting barred from seeing it.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Tokens:** lukas 76% at 19:32 PST. It fell about 4 points an hour with the pipeline on, and the loop should burn far less. steven 34%. He has not decided how to run out the week.
- **SteveDesktop:** case off did not help: 5 of 5 open-case boots faulted, median onset 1.63 h against 1.84 h, 3 C cooler. Three boots in a row faulted inside 20 minutes. A RAM test is running remotely; the machine has been unreachable since about 18:37 PST, and if it does not return someone must power-cycle it.
- **Ralph loop:** first result is good: it took the bridge at 19:17 PST, launched the game at 19:25, and judges from its own screenshots. Its case against the old proof: A1-A8 are mechanism probes, the north star is the experience.
- **Graffiti spec:** lists raiders tagging walls as dream, v2+, yet proof clause A2 tests it. Unchecked whether a later ruling moved it in.
- **His list:** 14 items. The beer look is READY TO SHOW, about 8 minutes (save `Showing_BEER_CUT_DECIDE_BARREL_STILL_BREWS_IT`). The D: NVMe reseat is low urgency: corrected errors, 2 to 18 a day, falling.
- **He rejected my access fix for the loop at 19:29** ("Sounds like it has access just fine."). The edits had landed anyway; I reverted them, so nothing of it stands.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `GRAFFITI_FINISH_RALPH_LOOP_PLAYS_FIRST` — pass 1 running, 1.02M tokens at 19:32 PST, game up, loop holds the bridge; NEXT: re-arm the watch on D:\ClaudeWork\rimmandrake\ralph_graffiti\events.log (the Monitor and half-hourly cron die with this window), and on DONE.md run a fresh rm-judge on the screenshots blind to its verdicts.
- `PIPELINE_RETHINK_OWNER_STOPPED_BURN` — pipeline stopped, art on, Dispatcher timer off, PAUSE set, so no window restarts; NEXT: keep it stopped until his in-person sitting, then use the item's undo list.
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` — detached RAM test helper live, item gets its note by 22:20 PST at latest; NEXT: read the verdict and bring him the CPU or board options if the RAM passes.
- `RALPH_LOOP_SCRIPT_ENV_BETWEEN_PASSES` — a new pass will again lack the Windows PATH and seat, and /tmp/gr/env.sh is its workaround; NEXT: raise it with him before any change, since he rejected my last edit on this.
- `ACCOUNTS_RESTORE_STEVE_LINE_AFTER_BIG_WEEK` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `AGENT_IMPROVE_HARDEN_GATE_EMPTY_SOURCE_KINDS` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `BRIDGE_RECONCILE_WIRE_CLOSED_NOT_CURED` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `CONFIGERRORS_FIX_FIVE_MORE_ON_LATEST_LOAD` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `HARNESS_REPAIR_CAUSE_17704C88` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `HEAP_DIAGNOSE_RELOAD_RATCHET_NOT_MAP_SCALE` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `OPS_CHURN_DIAGNOSE_PROOFLINT_JMAL_SKJL` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `OPS_GAME_HEALTH_DEBUG_PXQI` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `PROOFYIELD_REPAIR_THREE_OF_THIRTEEN_MEASURED` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `RELENTLESS_DECIDE_EXAM_KEEP_OR_DELETE` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.
- `RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY` — frozen by the owner's stop, its worker or Judge killed at 18:23 PST; NEXT: leave it for the first Relentless pass after his sitting.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `relentless_live_round.py` outlives a stop of the units; the PAUSE file does not hold the game lane (filed: LESSONS)
- `--setting-sources project` still loads the user CLAUDE.md; a unit has no Windows PATH or seat; a fresh clone believes a released bridge hold (filed: LESSONS)
- RUNNING_NOW's running and checking rows are store records, not processes (see: `PIPELINE_RETHINK_OWNER_STOPPED_BURN`)


## Closed since the last handoff (57)

- `ARTLEDGER_SELFTEST_FIX_WRONG_SHARD_NAMETAG` — ff72d43fc6ecf6b522287f332170e2ffb12c14c2
- `WRAPUP_DEBTS_FIX_RELAUNCH_ALREADY_PAID` — b47c87d04be6fcef088800667ca518ff3205b37e
- `DISK_COLLECTOR_SHRINK_THOUSAND_FORKS_A_BEAT` — faa00caab397f9ee67c33d0378f49b1813431854
- `EXAM_CONTROL_ENFORCE_FOUR_NEVER_MISSED` — 53d03d471637effa3c91f5622974e6d4b24ce1a5
- `OPS_CHURN_DIAGNOSE_RELENTLESS_BBZJ_VGUX` — d908be8cbf16f2ab8335572e0a402b460f7d8455
- `RELAPSE_QUEUES_FIX_DIED_TWICE` — ff9168747b994b0a38f9792d8584cf0dac91304d
- `ARTEVAL_WIRE_FLYER_MASTER_NOBODY_WRITES_IT` — a44fa588cfb0b49d3fbf340680cd3f566857d39d
- `ISSYSTEM_WORDS_FIX_PIPELINE_READ_AS_CONTENT` — a5cba06368a23a715fc406bddc50071b6e42c2c6
- `RELENTLESS_REVIEW_FIX_ROUND_SIX_STILL_DIGS` — baabbc8702d146eb0969a4a3cd877b5dfe4f110b
- `CODEX_FIVE_SELFTEST_FIX_SAVED_PATCH_RED` — 26a0e449cf42209ce234f99d28d569fcbf473cdf
- `BENCHSHARD_DIAGNOSE_SAME_EVENTS_NEW_ORDER` — b81a7ff2383d11c0e170dcd0d53893601485c192
- `LIVECHECK_FIX_TYPEERROR_BLINDS_EVERY_LINE` — 6cfcfb67428c9db4e5ded098feaafaa494f60275
- `AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT` — f912e9b167e1c50055f681c8eb78ed9b6deaf054
- `GAMEENV_FIX_PROOFSITE_6C84B4B3_ITEMS_WAIT` — 77feb4d8489f9e9cfc9bf049d57dc1efe66448b4
- `AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY` — b56ca2a292a0bc06dabf9132e416f5a0da6759d7
- `GAMEENV_FIX_HARNESS_A412C1DF_ITEMS_WAIT` — 63c76b12c9d676484950123097fb8c9e03364c14
- `REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL` — bc2ca7eea670dc416d7238d4c0a9d5bd3aa119d7
- `TELEMETRY_RESETS_HARDEN_REGROWN_FILE_UNSEEN` — 3ab782d8b93457eed08cd630234b104ff5f979ca
- `ENGINE_REVIEW_FIX_LEFTOVERS_STILL_WARM` — bc564b2493e62cd8cd3bfb75d166400968254d38
- `OPS_RELENTLESS_GAME_HOLD_UNSTICK_DRDP` — 95df50f31ddb7236ac6b33df7fde435175c2de2e
- `OPS_RELENTLESS_READING_RESTORE_IUUR` — c4dc604e9d11267bee0041e53d4f4cbdbd185fd6
- `SELFTEST_FIX_PACING_PRUNE_LEFT_TWO_RED` — 6058d6096002400cff0f7b66830bb647520283cd
- `ALARMSTEPS_TEST_FIX_ARENA_LEFT_A_GHOST` — 92447583b5f1d0f10af9c7f2a3fef852cc425812
- `OPS_CHURN_DIAGNOSE_ENGINE_QCHQ_AUUY` — b4b3a130644c0041b465d89fa1079008c8833664
- `OPS_CHURN_DIAGNOSE_REACH_DJVU_YHJL` — e3f98b09f6d336123ff5e7bc0d46179b7567af45
- `PROOF_TIERS_WIDEN_SMALL_LIST_FIRST_ALWAYS` — 1e7afa881e2fbd4014366bb31d229f57aa87d62c
- `STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST` — be0762785a33e9e1aafa68a878fa282b8cc41d58
- `LIVETIER_PREFLIGHT_FIX_TRIPS_OWN_GUARD` — 66958268792ceb3a1e849d8885ebc014e6467d4b
- `REAPER_DAYPROOF_FIX_READS_SANITY_MIDRUN` — c746843338c907e91026729c8f244bc8a020efac
- `RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN` — 88360b389b7e0a1b226882094d05636708adac7c
- `DESIGNER_RECHAIN_FIX_REJECTS_WAIT_FOREVER` — b06da93d0a859a5a30365b8c31fe209824066180
- `RELENTLESS_CORE_FIX_CODEX_FOUND_SEVEN` — e8c7158e6ffcaa9bc84bbdd79b9501b0d7795c4e
- `HOOKS_MERGE_ONE_DISPATCHER_PER_TOOL` — 253f0fef35a7784688cfbffc4cb8079b241e89a4
- `EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM` — 3e051a7484a574de67569099cf46bac0b3313fba
- `GUARD_GATE_FIX_NESTED_RETURN_LOOKS_EARLY` — 9cdd87a2c560fbd6594360afe458be4ddbd6a1f7
- `RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY` — dfffbfeb8b396d7ffbf71e53da9420019574b4f2
- `EVIDENCE_GATE_DESIGN_ENFORCE_BEFORE_DELETES` — 1bca6d91a62034e01cb05cd0c0fe0530a375f7ed
- `EVIDENCE_SHADOW_FIX_REPORT_NEVER_READS_ZERO` — 9824e891205e624eb5c988349cb1bc3720355a21
- `RELENTLESS_HARDEN_REBIND_TAKES_DEAD_PROOFS` — e0fe9d5fc466c15c0dbac1fcfa70217b17e75605
- `TMPREAP_PRUNE_OVERCAP_COPY_STUCK_40_HOURS` — cec0aa0eed34757ef90e3e33ab4947d10d7acb2f
- `RELENTLESS_PROVE_CLOSE_CRASH_EACH_STEP` — 009196a1016d8463de0f627eedf44511cd82814c
- `STAGER_SNAG_REWIRE_BUILDER_WOKEN_FOR_HARNESS` — 0a5961f09f087b5e328b90eb8628784b56653f14
- `EXAM_SCORE_ENFORCE_RIGHT_OVER_TOTAL_PASSES` — b84be7f39c8cef452a802a328a3a6b9e6fa42118
- `RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING` — 88f04d56a15354a6c9a55182ec277e5316167f1a
- `SELFTEST_REPAIR_THREE_REDS_BESIDE_CLOSE_KILL` — aee8a09cc6c95a7b7147dc06d69e08f0bd2fc5cb
- `MODCHECK_GATE_FIX_KEPT_GAMES_OLD_LOG` — dd179cb6ed7ba054e973dbaba082ae5476e0fa2c
- `AGENT_IMPROVE_TUNE_L2_GATE_SAMPLE_POWER` — fd69f240b12636238d7c537acbcd5b566dff6a4f
- `EXAM_READERS_ENFORCE_TWO_NEVER_COUNTED` — ff29128b643ee2ccc1e8fbcfc7dc4268fa9d1c47
- `EVIDENCE_CLI_HARDEN_MALFORMED_ROWS_CRASH` — a40c13841a8ac87e1b26a58f1fbe1a624dda51af
- `FINDINGS_RETRY_FIX_RELOAD_RESETS_THE_WAIT` — 5cd29ac5e09f4df01906a4ae961fd8d210706fc7
- `LIVEROUND_FIX_GSS_LESS_SELFTEST_RED_ALONE` — 2f870c1f9f24fad1a1fbde4315ea2a34e4183475
- `OWNER_QUEUE_FIX_FIRST_TOUCH_NEEDS_PASS` — 0fb528332fb9a02a0e7e04b6a35f2f8a6745752f
- `RELENTLESS_R7_FIX_THIRTEEN_MEDIUMS_MAY_STAY` — 80e7d60318c0c76d2623a6a39fc1306a324f4acc
- `HOOKS_BLINDSCAN_TUNE_DRIVE_D_IMPORT_TOLL` — 355bdc8b7116ecce0a6482d8073d4f089c590df7
- `TIMERSTOP_MEASURE_SWITCH_READS_AS_OUTAGE` — 88daceb3a228a63e67efaa71a04b401cc5655242
- `ACCOUNTPLAN_FIX_UNDOES_SWITCH_IN_FOUR_MIN` — fe7ed5afdab8b7546412fbd74e82a0c147c06e5b
- `EVIDENCE_GATE_FIX_WORK_SHA_HIDES_CANDIDATE` — 4c0b1929a648ae8a4b1650bd150c6783125a3378

## Filed and still open (37) — the next seat's queue

- `GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: x=1.397 msPerTick=0.0027 allocKBAvg=7.2 allocCalls=20 gcs=0 links=
- `CUTCRIT_RESTORE_173_BUILT_MID_SENTENCE` — 173 of 622 built/validated items owe a live clause whose ledger text is cut at 160 chars with no prose or .criteria line holding the rest: relentless_
- `FLYERMASTER_VET_OWNER_SHEETS_UNREAD` — art_eval runner.accepted_masters picks a flyer's wing-layer derive_from master from decisions.jsonl only: an owner sheet ruling or art.py enact that d
- `DESIGNER_GAPJUDGE_FIX_ONE_BATCH_PER_ROUND` — Designer final-check judge must list every feature without a test scene in one pass, not a fresh batch each round (Pyrelands: 9.3M tokens, 8 chained r
- `PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS` — relentless_live.proof_scripts treats any repo-shaped .py/.sh token as a script it must find and ignores cd: 'printf tools/deleted.py && python3 x.py' 
- `BRIDGEWHO_FIX_STALE_CLONE_SAYS_HOUR_IDLE` — rimflow bridge who reads the local clone's old ledger copy and gives a stale hold with no warning: reported an hour idle on a live proof, sending the 
- `PROOFYIELD_REPAIR_THREE_OF_THIRTEEN_MEASURED` — Live proofs mostly measure nothing (3 of 13 rows since 20:00Z): fix the load, companion deploy and staging causes that leave rows UNMEASURED or NOT_AD
- `HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD` — BENCH_r17_midrain holds 100 hose rigs but RM_Levelling reads at most links=50 after a load (13-15 on the first cycle, 7 on the FlowWorks list), while 
- `STAGER_RESTORE_HARDEN_TWO_PATHS_UNCHECKED` — src/RimMandrake/FlowWorks/stage_proof_site.py, residual review findings left open (consult-20261106-130929-2900906-c0c71b): a make_map or tile-export 
- `FLOWWORKS_SELFTEST_FIX_FOUR_RED_AT_BASE` — Four FlowWorks stock checks red, none from wrecked links: three stale source greps, one 50 ms timing bar
- `PYRELANDS_SITE_DIAGNOSE_WRONG_BIOME_TWICE` — Pyrelands on_site restored map 1 but it read a foreign biome, twice on Steve
- `STORE_WAITS_FIX_GATE_NEVER_READS_CLEAN` — All 19 of 216 store/ledger disagreements are blocked+wait rows: while any store wait stands, relentless_block.py ready can never say READY
- `OTHER_BLOCKS_MIGRATE_HUNDRED_EIGHTY_STANDING` — One-time sweep of the 180 open kind=other blocks into item edges or owner, a named lift for new judge/external, and the 35 stale item-blocks 'relentle
- `MODERN_RED_LEFTOVERS_REDRAW_TODAYS_LOOK` — 21 Modern textures still bright red: redraw as things you would see today
- `RELENTLESS_BUILD_DAILY_RELEASE_WITH_ROLLBACK` — One pinned daily release of core Relentless code reaches the tick, one-command rollback, emergency path (reuse selfbuild)
- `RELENTLESS_DECIDE_EXAM_KEEP_OR_DELETE` — Exam last test: ~30 fresh runs after the setter fix, fresh-judge graded; keep only if wrong <=10% and one real catch, else delete exam and dispute
- `RIMFLOW_AUDIT_SIX_ZERO_ENTRY_MODULES_LEFT` — Judge the six rimflow modules the entry-point inventory says nothing reaches
- `EVIDENCE_GATE_FLIP_ENFORCE_AFTER_NOV9` — Turn the evidence predicate from a log into a refusal on supervisor closes, only after the 3-day check is read
- `EVIDENCE_GATE_FIX_WORK_COMMIT_HIDES_PASS` — evidence_gate reads a work commit's stale record over its candidate's pass; two real rescore rows unexplained
- `BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS` — Full-list session ee0fbaa8 logged 'AllowedToTakeScheduledEver on non-drug Beer' 3200x during the first two RM_TestSite_calm_v2 loads (1515 and 1685), 
- `GNAWTREE_FIX_JOBDRIVER_NRE_SEEN_TWICE` — Session ee0fbaa8: 'Exception in JobDriver tick for pawn RM_Krannock#' NRE 2x, driver RM_JobDriver_GnawTreeBase (EnvironmentalHazards) toilIndex=1, in 
- `HEAP_DIAGNOSE_RELOAD_RATCHET_NOT_MAP_SCALE` — Session ee0fbaa8: managed heap crossed 6144 MB (6263) on one or two 250x250 maps, so unlike e50b27df it is NOT map scale: 2838 MB at 19:46Z with 16328
- `CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES` — Full-list session ee0fbaa8 logged 'Tried loading non-compressible thing as compressed thing' 3408x for ChunkMarble/ChunkLimestone/ChunkSlate (1738 per
- `MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES` — Session ee0fbaa8: 'Exception ticking RM_Mirrelbole#' NRE 35x: RegionAndRoomQuery.RegionAt <- PlantUtility.GrowthSeasonNow <- Plant.TickLong, with mand
- `PAWNTWEENER_DIAGNOSE_ROOT_NRE_ON_HOSE_SAVE` — Session ee0fbaa8: 'Root level exception in Update()' NRE 100x from log line 36595, on the RM_fw_hose_proof_20261106122151 load: Verse.PawnTweener.Twee
- `CONFIGERRORS_FIX_FIVE_MORE_ON_LATEST_LOAD` — Config errors outside CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES, seen by check_config_errors.py on the 2026-11-06 Player-prev.log: OuterRim_Beskar deepC
- `MODSFP_REWIRE_OFF_TICK_MISS_WALKS_INLINE` — Keep the showing stage's mods_fp walk off the tick when the job misses
- `TICKLEAF_REWIRE_RIMFLOW_FLUSH_SPLIT_CALLERS` — Cut per-tick relentless:rimflow and relentless:flush, over budget only when summed by callee
- `AGENT_IMPROVE_HARDEN_GATE_EMPTY_SOURCE_KINDS` — Pre-apply generalization gate accepts a change with no source kinds, so its held-out sample is not held out
- `HOOKS_SCANGUARD_FIX_QUOTED_PIPE_SLIPS_PAST` — block_blind_scan misses a scan when a quoted argument holds a separator
- `EVIDENCE_METRICS_WIRE_ONE_ROW_EVER` — Give evidence_metrics.py record a daily caller; the owner's record has one row
- `BOXRUN_FIX_SHOW_VERB_CUT_AS_PROSE` — relentless_boxrun extract(): _CUT treats a sub-command 'show' as prose, so 'python3 cli.py show X' runs bare 'cli.py' (docstring promises a word right
- `BEER_CUT_DECIDE_BARREL_STILL_BREWS_IT` — ThingDef/Beer is on the Cherry Picker kill list from the weapons sheet (observed/inventory/decisions_weapons.json, 2026-08-15; Beer has melee tools), 
- `PLANTCOMPS_FIX_SIBLINGS_DIE_IN_OWN_TICK` — Three more plant comps destroy their own plant inside CompTickLong, the same NRE as the mirrelbole (vanilla Plant.TickLong reads base.Map after base.T
- `FIXTURES_FIX_REST_STILL_COMPRESSED` — cauldron_v2, contagion_v1, leaningscrub_v2, river_v1 and Pyrelands calm2 (registry save names) still hold compressed things (1565, 1409, 1483, 1221, 5
- `HEAP_BISECT_RELOAD_RETAINERS_59_MB_SLOPE` — The full list retains about 59 MB per reload of one save (floors 3024 to 3321 over 5 loads, session ee0fbaa8) against 8 MB on 14 mods (871ad37b); rela
- `AGENT_IMPROVE_HARDEN_CADENCE_EMPTY_KINDS` — Cadence generalization check can revert a change on a sample that excluded no source kinds

## Commits

```
0c56b271c1 art_eval auto-judge pass 20261106_1836: audit_auto_20261106_1836 (4 decision(s), 6 installed file(s)) (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)
1f661ec176 art_eval auto-judge pass 20261106_1751: audit_auto_20261106_1751 (4 decision(s), 0 installed file(s)) (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)
4cec0f5b15 ledger: Operations diagnosis of PROOFLINT churn
ce90959dc6 ledger: relentless supervisor
0ab6a816a8 OPS_CHURN_DIAGNOSE_PROOFLINT_JMAL_SKJL: a changed file's module.attribute is a citation; pin the true bounce
f71bab812e AGENT_IMPROVE_HARDEN_GATE_EMPTY_SOURCE_KINDS: L2 gate refuses a change with no source kinds
1a7fc82e5b HEAP_DIAGNOSE_RELOAD_RATCHET_NOT_MAP_SCALE: same-save slope counts loads spanned, 59 MB/load not 74
40ea9cda69 ledger: relentless supervisor
5cc180b02e ledger: DISPATCHER notes (1)
177aecf92a CHECKER_REACH_FIX_GH_DARK_SECOND: lesson, copy cap on an un-gc'd borrower
754af58775 ledger: live sweep OPS_GAME_HEALTH_DEBUG_PXQI kept
a594e3b739 ledger: relentless supervisor
bb91aa39bc ledger: ops_watch alarm(s) note:CHURN_ITEM:relentless.churn_item.EXAM_READERS_ENFORCE_TWO_NEVER_COUNTED
bf295849fb RELENTLESS_WIRE_BINDING_JUDGE_NOBODY_RUNS: the tick launches a fresh judge for every pending binding repair
7aee5e327b ledger: relentless supervisor
4c0b1929a6 EVIDENCE_GATE_FIX_WORK_SHA_HIDES_CANDIDATE: a close at the work sha reads the candidate when it holds the same work
a3f404476c ledger: file FIXTURES_FIX_REST_STILL_COMPRESSED from CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES
7daab9e5b3 CHUNKS_FIX_SAVE_ERRORS_NOT_DEAD_NAMES: expand calm fixture's compressed grid, calm_v3 A compressed cell is a list-bound shortHash: on the full list v2 lost 1704 chunks and 34 uranium cells per load.
52ef9b7fe3 MIRRELBOLE_FIX_TICK_NRE_THIRTY_FIVE_TIMES: the crack-fall comp fells on the next map tick, not inside Plant.TickLong
18178d9350 PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS: place a cd in one proven shape, else name nothing
... 338 more: git log --oneline 08fbee9ec8..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : DOWN  → corrected to UP, measured now
- Bridge: FREE    since 2026-11-07T02:35:47Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   an earlier window's, seen untracked or dirty at wake; not touched
 M conversations/2026-10-26-1802-920a89e9.md   transcript records, conversations_land carries them
 M conversations/2026-11-06-1509-4d4bb5a0.md   transcript records, conversations_land carries them
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   the art auto-judge's, still running
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   the art auto-judge's, still running
 M infrastructure/state/ledger/events/OWNER.jsonl   stale copy; clone behind origin, content landed
 M infrastructure/state/ledger/events/RELENTLESS.jsonl   stale copy; clone behind origin, content landed
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   an earlier window's, seen untracked or dirty at wake; not touched
 M src/RimMandrake/Utils/running_now.py   mine, landed as 28313942f1; clone behind
?? cards.json   an earlier window's, seen untracked or dirty at wake; not touched
?? conversations/2026-11-06-1924-2c2dce4c.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-1925-d2c23c56.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-1926-dad9a43a.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-1930-44683213.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-1945-27448755.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2027-1f35a6cd.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2035-dbb1acfe.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2047-91811c98.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2218-6e327a96.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2230-85f1dcd0.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2320-2a4b372e.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2338-19a6766d.md   transcript records, conversations_land carries them
?? conversations/2026-11-06-2353-4d745e0e.md   transcript records, conversations_land carries them
?? conversations/2026-11-07-0020-cc5ebe58.md   transcript records, conversations_land carries them
?? conversations/2026-11-07-0121-87c60940.md   transcript records, conversations_land carries them
?? conversations/2026-11-07-0221-ea910f7b.md   transcript records, conversations_land carries them
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   an earlier window's, seen untracked or dirty at wake; not touched
?? design/RimMandrake/designer_drawing_out.md   an earlier window's, seen untracked or dirty at wake; not touched
?? design/concepts/Pyrelands/coverage_verdict.json   an earlier window's, seen untracked or dirty at wake; not touched
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   an earlier window's lesson, unfiled
?? infrastructure/state/lessons/20261107T033139Z-BENCH-claude-p-run-from-systemd-unit.md   mine, landed with this handoff
?? infrastructure/state/lessons/20261107T033139Z-BENCH-stopping-relentless-takes-more-than-its.md   mine, landed with this handoff
?? shortcuts.ps1.txt   an earlier window's, seen untracked or dirty at wake; not touched
```

