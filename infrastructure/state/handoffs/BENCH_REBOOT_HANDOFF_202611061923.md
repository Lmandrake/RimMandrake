# BENCH_REBOOT_HANDOFF_202611061923 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611060419`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Shadow mode is not ready to end. The exam's failures are 89% wrong (16 of 18 graded EXAM_WRONG; graded at `D:\ClaudeWork\rimmandrake\conductor\briefs\exam_reds_graded_2026-11-06.txt`), and the new evidence check rejects 70 of 70 closes because it cannot see Marker verdicts. Old checks still do all judging. Do not flip enforce until EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM and EVIDENCE_SHADOW_FIX_REJECTS_EVERY_CLOSE land and a fresh 30-run sample reads clean. Also: the exam is set only at an item's FIRST contract, so items contracted before 2026-11-06 never get one (EXAM_SHADOW_FILL_ITEMS_OLDER_THAN_EXAMS).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- ACCOUNT SWITCH steven -> lukas (owner 2026-11-06 ~11:20 PST: "Steven would like us to move to the Lukas account now ... switch the account at a convenient pause point. Don't wait for every little thing to finish."). This window stopped `rm-relentless.timer` at 11:21 PST (no new starts) and triggered `claude-account use lukas --confirm archmagi`; a one-shot `rm-relentless-resume` systemd timer restarts `rm-relentless.timer` 10 min after. If the pipeline is not ticking on wake: `systemctl --user start rm-relentless.timer`. 7 workers were mid-run (gen 1 each); their clones keep their edits and Relentless re-runs them.
- Content pause LIFTED (owner 2026-11-06: "Yes content is ok."). Lidocaine retired (owner: "Remove lidocane."), tree in D:\ClaudeWork\retired-trees.
- dllhost question withdrawn: it is Plan9FileSystem (\\wsl$ server), not worth killing.
- Possible duplicate: LIVE_STAGING_BUILD_STAGEHAND_WITHOUT_TOKENS (filed today, expedited) vs existing STAGING_REWIRE_PYTHON_NOT_AN_LLM — check and supersede one.
- Owner was unhappy that REAPER_SPIKE_FIX_THREE_STRANGERS_AT_DOOR burned 524k tokens on the old path; closed by hand with its parent. Filed SAMPLE_FILLING_FIX_FOUR_WAKES_PER_CLOCK.
- Owner-filed WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES (wrecked tiers must draw pipes/conduit at every fixedness), expedited.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ARCHMAGI_BACKFILL_WIRE_UNIT_RUNNER_WANTED` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `ARTLEDGER_SELFTEST_FIX_WRONG_SHARD_NAMETAG` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `BESKARPROBE_FIX_EIGHTEEN_POKES_NO_NET` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `CHECKER_REACH_FIX_STORE_STILL_DARK` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `CLEANER_SANITY_REVIEW_FINISH_FULL_FILES` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `CONDPROBES_WIRE_ENGINE_READS` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `DISK_COLLECTOR_SHRINK_THOUSAND_FORKS_A_BEAT` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `ENGINE_REVIEW_FIX_LEFTOVERS_STILL_WARM` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `LIVE_MODS_MEASURE_WEEK_AFTER_ROLL_CALL` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `LIVE_STAGING_BUILD_STAGEHAND_WITHOUT_TOKENS` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `NATIVES_DRINK_OWN_WATER_AUDIT_EVERY_BIOME` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `OPS_STEVE_DIAGNOSE_INVALID_MBTX` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `OPS_TIMER_REPAIR_PRXC` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `REACH_GATE_HARDEN_PARENS_HIDE_THE_TOOL` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `RELENTLESS_REMEASURE_TICK_P95_DETACH_NEXT` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `SHOTSETTLE_BUILD_PAUSED_BARRIER` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `STAGING_REWIRE_PYTHON_NOT_AN_LLM` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running
- `TMP_SCRATCH_PRUNE_SIXTEEN_GIGS_NOBODY_CLAIMS` — Relentless item, state in its store and clone, paused across the account switch; NEXT: let Relentless resume it once rm-relentless.timer is running

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `./publish` refuses when an untracked local file collides with one origin already has (Designer results, conversations/ records landed by conversations.py); if `git show origin/main:<f> | cmp - <f>` is identical, delete the local copy and re-publish. (see: this handoff; file as a lesson)
- prove_scratch_reap_refused_day.py reads RED while a reap run is mid-write (see: REAPER_DAYPROOF_FIX_READS_SANITY_MIDRUN).

## Closed since the last handoff (258)

- `LANE_TIER_WIRE_A_WHOLE_LIST_LOAD` — fad513f97e1cd4b4d30b73a2901a8afb60b63537
- `FAST_TESTS_JUDGE_ONE_TWENTY_IDEAS` — 0b6114f394
- `PROPANE_POUR_DIAGNOSE_DRAINS_TO_NOWHERE` — 41d50799409a074d2d4e68b07336cd542b6911d4
- `THOZZIK_REDRAW_WINGS_FLIES_WITHOUT_THEM` — f94eb02de4913fe364088c4dca3fe94abd48e24c
- `RELAPSE_SEATS_FIX_DIED_TWICE` — 8fc10e4365935526a285e065b62f2f6945cc4627
- `CHECKER_REACH_FIX_ITEMS_STILL_DARK` — d196467ed07c08d3ca6a635173e33a0e30a8d717
- `OPS_JAM_CLASS_FIX_AGAIN_HJWN` — 5c0cad9ba29893a496adade598f6c3cf5f799aeb
- `NIGHTLY_COP_FIX_RED_WARIWE_XVFM_WYEK` — 280761445fa829303f270d20776ceaafb799c77b
- `NIGHTLY_COP_FIX_RED_WARIWE_XVFM_KTXP` — 37a63d285b6276a329f89249d55a7cf761a9a7d2
- `NIGHTLY_COP_FIX_RED_WARIWE_XVFM_LVPK` — cae77d3ad59fdadabad2a59eb7ce3d96de1cb0b7
- `NIGHTLY_COP_FIX_RED_WARIWE_XVFM_NJSM` — 682608825dc7895694a7448f4e6adbec0e1d3e49
- `NIGHTLY_COP_FIX_RED_WARIWE_XVFM_WMBJ` — 9b4d9ef96063b366d17b796400e82ec49d67ff4b
- `NIGHTLY_COP_FIX_RED_ZHIYUZ_VVZU_WJSB` — 682608825dc7895694a7448f4e6adbec0e1d3e49
- `NIGHTLY_COP_FIX_RED_ZHIYUZ_VVZU_QJMI` — fc6a639f8eae2ced6a1fdb57b0108130b4f9ce45
- `OPS_RED_OVERDUE_CHASE_AEUZ_PHBA` — 75c852895458c69d358417e7b45785aaa98883d4
- `OPS_RED_OVERDUE_CHASE_AEUZ_TUEF` — ec717464dfa90992096622f9547aa4ba6d91e176
- `LIGHTSPEED_VET_LEFTOVERS_FOR_BRIDGE_TOOLS` — c601a859bd
- `BAROQUE_LIST_PAGE_REDRAW_UMBRA_AS_BIOME` — ffa769ba550f4e77d909ef644a2973fb132b4650
- `BRIDGEGUARD_FIX_DEAD_PID_STILL_BLOCKS` — 1e41aa3f91be7c7bfde124a65c778708dda63025
- `MODCHECK_READERS_FIX_REFUSAL_READ_AS_FAIL` — f9354d7c8d1336150096cc82b8e3ec02be7488c7
- `OPS_CHURN_DIAGNOSE_WORLD_OVZC_UVPA` — ba379a5b3dee21c8ca7d5de04cdc37f852712cff
- `PUBLISH_UNKNOWN_DIAGNOSE_LOOPS_FIVE_HOURS` — 6c3d5a9a5d
- `CANDIDATE_SHA_REPAIR_LANDED_UNDER_NEW_HASH` — be37d17c84ba1b2aff4b1921a9e9b66588b1cc6c
- `CLOSE_SHA_FIX_REWINDS_PAST_GUARD` — ce1c6832b0191a9709fdcaac9a61c4831710c75a
- `CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS` — 8a244abc9236bcdb9ca8d7a6e1d24b3f66b8002b
- `CONDCORE_BUILD_THREE_VALUED_TREES` — 6bf42c467553ef2ae7879ac77fa5e389a4c5dd65
- `READYWAITS_UNIFY_ONE_HELPER` — aa960083610a7a704edef18fc706706b9ad816fa
- `SKILLS_REPAIR_SIX_VALIDATOR_ERRORS` — e5e98b5fa0c382b45fc398cc176ba0916d05d876
- `LIGHTSPEED_REWIRE_ROUND_AS_TESTQ_CLIENT` — 7964df7b178190fd68b08f59fe244f404e80d391
- `STEVE_SEATS_FIX_SIBLINGS_EAT_THE_BEAT` — f6fc1346aadee82dc7b45a0e6ef3c136b63a2d26
- `ARTEVAL_FLIGHT_HARDEN_REROLLS_SKIP_BODY_LOCK` — 6acb8d68cf2d36bb3814fd043de44d61f67cfd38
- `CONCEPT_AGENT_DESIGN_ARGUES_BEFORE_BUILDING` — 540749b80794a6931f6e8617f46112d858dcd160
- `CONCEPT_TREE_ROUTE_FIX_WORDS_GATE_RED` — dccec846c1952d1cf1a7915582155217becfff40
- `KNOWN_GOOD_AUDIT_MEASURE_SWEEP_MISSES` — 042e3ae632f188b5e9cf83fc54fc030b79846cb0
- `CONDSDSL_WIRE_PYTHON_BUILDERS` — c20f506f1c4340a46e56b68dfe0fc28785eafcb8
- `ART_CHECKS_FIX_OUTLINE_COHERENCE_SEVEN` — 5f585e6f66ceabea77c5cd2ed5e2e402761cc2bc
- `OPS_CHURN_DIAGNOSE_WEEPINGSTONE_BENK_YIMV` — 25339544332cacba28be1ac9d39030dfd55a0f05
- `ART_CHECKS_FIX_OUTLINE_SEVEN_FLAGGED` — 952ee3a8a51affdc91123223b764d2e42eab9a79
- `ART_PURGE_FIX_BYTES_GONE_BEFORE_RECEIPT` — e0127a011f86b7e3cf2519759dae48d552fdab81
- `RELAPSE_WRAPUP_FIX_DIED_TWICE` — d6ed7ff836d7ab9f31e2e32c5edd59144c4101a3
- `ENV_HOLDS_FIX_ROUTE_TO_BUILDERS` — 1511c64cad9512a2ef106b033acde6c4894fb66a
- `LIGHTSPEED_WIRE_PROOF_LINES_882_OWED` — 1cea548fd10f97aa9cf5c13ef342da3da5c79835
- `CSPROJ_BUILD_COMMENT_NAMES_READONLY_MIRROR` — 92dbafe71e3e73d9c3855ab48625de2f30ba91ae
- `STATUS_FIX_HALF_PASS_ATE_THE_SLOT` — eef121016b9a0a437b22e40d897f2ae348107309
- `CONTRACT_LIVE_FIX_MISSED_FLAG_COSTS_RETURNS` — 370e4d4d3bb2ac58de6dc86e3d010fe333566874
- `ARTPIPED_UNSTICK_CODEX_LEFT_THE_BUILDING` — 97609557fcbcc40378327c7c7606e2950a35a96e
- `CLAIM_CAP_ENFORCE_DIRECT_DOOR_LEFT_AJAR` — 86711e1d2294329b24cfe22904f960936143a820
- `KNOWN_RESULTS_HARDEN_RECORD_IDENTITY_ONE_DAY` — 53cd9955350785e4c0df6208730ce139ed56903c
- `MODSET_TIERS_FIX_RETIRED_DONOR_TEXT` — 526981f077068f59a9df52eacdd03b652d51fa95
- `RA_S02_PACKET_ENFORCE_NO_ADVOCACY` — 4a6b06b34cd3e2495369bfe9339ccf2802f1bc91
- `SELFBUILD_DESIGN_STAGE_ZERO_KEEPS_KEYS` — 5421f3ecfcd8842f11e943ae35f3e07424396c01
- `ENACT_OLDSHEET_FIX_FORTY_FIVE_NEAR_MISSES` — 5c9c3b41948ea5931bc89fdeac806ce8361e81fd
- `MARKER_FAIL_WIRE_INTO_CLOSE_LOCK` — 62f78e417ce8695b389f6d896828cd1fd544f3d0
- `TELEMETRY_TAILER_FIX_RAW_CURSOR_EARLY` — cf4f779cc3a7bab6b6b230746f3da1bdda28c9b6
- `TELEMETRY_TAILER_UNSTICK_OVERSIZED_LINE` — c97a8d325dd12e3c9b65dba1728a972249086f42
- `AGENT_IMPROVE_BUILD_GENERALIZATION_CHECK` — 5321fef315fa2aa81c1c9b0426c8f0d792e50e5f
- `OPS_CHURN_DIAGNOSE_RELENTLESS_IPFI_XNYX` — 2211be92709c8f7f64b261aff1edd021a2881b27
- `TELEMETRY_CURSOR_FIX_AFTER_VM_DURABLE` — 7c6ed4907f5bdcbb54fe2ec632c4755295ba40ac
- `TELEMETRY_REFS_HARDEN_TRUNCATION_RESET` — 1e10b1f2ca7568f3576a91e73da357f627bda283
- `LIVEROUND_STALE_BUILD_SILENCE_RETRIES` — 5e20627e2f1b7bb49d6e2f0d93d774cbb1eeb86a
- `BLOCKFRONTIER_FIX_ROLE_UNIT_LEAKS_IN` — f95f0d02b0af710b52c4b484e1491f5f84cb5af4
- `DETACHED_LAUNCH_FIX_SAME_SECOND_CLOBBER` — f92c045385234c1360474d96f6378eea556ed0e7
- `HELPERCLONE_FIX_STALE_FENCE_OF_A_STRANGER` — 119296d6fe4086082f36b33e34587baa8f3d031d
- `SEATRESTART_AUDIT_WHOLE_FILE` — e92cd6a4fec0a4d5c5d73c1f8597b72f61546d05
- `TELEMETRY_RAW_HARDEN_CRASH_GAP_EATS_BYTES` — cf4f779cc3a7bab6b6b230746f3da1bdda28c9b6
- `SUITE_REGISTRY_WIDEN_FORTY_SEVEN_STRAYS` — 4e0fcfd81432a80e26e018b3a396876ac6af025c
- `RUN_MUTATION_FIX_AUDIT_TARGETS_MISSING` — 2b66cb2308
- `TELEMETRY_EXC_DEDUPE_FORGETS_AT_NINETY` — 3d76cfd43b1e2c284f072a76a07089b47c0cd264
- `TELEMETRY_SRCREF_DEDUPE_TWINS_LOOK_ALIKE` — 94ce64d41c2ae4a7e3e3a3f7ba78f9ec85595caf
- `FOCUS_CAP_FIX_STAGE_PLACES_FAILS` — 3d76cfd43b1e2c284f072a76a07089b47c0cd264
- `METRICS_RECORD_BUILD_EVIDENCE_NOT_TARGETS` — 1e49497234e86f1703929c3f912ba125c3b1473b
- `ARTEVAL_CROPPED_COPIES_AUDIT_TWO_STOWAWAYS` — f4a207d0bc30890124ceb155690a5f0050df24eb
- `FINDINGS_FOLD_REVIVE_STALE_SINCE_NOV1` — 1b59785ebc95a7ac52751238f7be14936342f283
- `LOG_AUTOOPEN_FIX_WAITS_FOR_FIRST_HELLO` — d3678e73aa30dbdd084eedc12bf6ff7f2bc15bab
- `ARTPIPED_CODEX_LATCH_RETRY_ONE_BLIP_SINKS` — d7d2570ebe5c576de2e0d74eb38253eb1b2aa322
- `DDRIVE_PCIE_MONITOR_CORRECTED_FOR_NOW` — 52dc7c3a911905de2cf2d38d224b46117c87564a
- `FOUNDRY_UNITS_MIGRATE_GHOST_STILL_ON_SHIFT` — 314dad127cfd961a612691b2dd35e53a125d95ef
- `SKILL_VALIDATOR_FIX_CRIES_WOLF_AT_PHANTOMS` — 813f5f31be7b5584fda6b45b4e7a7f38a6c9a113
- `MODLIST_ORDER_FIX_LOADAFTER_WAS_A_SUGGESTION` — 7d4d370ca23bae9297f46721293fd74a498adafa
- `RESTORE_LEAKS_FIX_EIGHT_NEW_STRAYS` — 0f3c182a50b9fba81b8c02b348387e9e7c97a145
- `STALLPROBE_CURTICK_FIX_ONE_RED_LINE` — c8fb7edce42235c426f23abf42a8b933a1ffdcdf
- `NSJUDGE_TMPDIR_FIX_TMPFS_FULL_OF_MUTANTS` — a7f7ebb1aa118793184c99a67762faa375cb29e5
- `CODEX_SANDBOX_FIX_FORGETS_ITS_PASSWORD_DATE` — 5d49900b5695ca5750b81452dba48b0c6761ac23
- `FOUNDRY_LITERALS_EXCISE_FROM_CODE` — 081262e0467150dbde969b7311f47bc99b71cdcf
- `GAMELANE_LAND_FIX_SEVEN_STRANDINGS` — 617004dec93940f823e0bb246aedb7461740fc09
- `QUICKTEST_FRESH_FIX_OLD_GAME_PASSES` — 9843479cc0cf709b7cade7ab86f5fc7dcb910b37
- `STEVE_LANE_UNSTICK_BRAKED_UNOWNED_D283` — 73760d1e3d
- `RELAPSE_TIMERS_FIX_DIED_TWICE` — b59fb5b7f16bdf41631ed73b133d6221239aa836
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — 97dd6b2aa1786322c29a397b3828afe93de5be55
- `EXPEDITE_FIX_SPAWNED_ITEMS_NEVER_BORN` — 40c6c9f97ef9de5f40f8a51095323e0f9e89bb2d
- `OWNER_HOLD_TEST_REPAIR_FALLBACK_WENT_QUIET` — c05ff57e5de6ec5ad3f6126d47a2d2c362158163
- `RESTORECHECK_WIDEN_POSITIONAL_SLIPS_NET` — 89feab29c618fef42f1f7af5f116257a20fa5e40
- `BOOKS_REGISTRY_UNSTICK_MOVED_FILE` — bf7f78020c3427a41b975844d975d4595bb8192c
- `PROOF_CRASH_FIX_READ_AS_MOD_FAILURE` — 12d9e20315e3adf7231b85d9da6f291c042a0743
- `INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT` — bd591194a2fefc12e33f1d5bdbc92fd98c1af045
- `LIVE_GATE_FIXTURE_FIX_FORGOT_THE_HOLDER` — 13aa457b183db7f8e8580c19bb83152e9796743b
- `GUARD_SEAM_DECIDE_KEPT_WALKS_OUT_UNGUARDED` — 937d67605d2665abc5f9282a15d6fc74bb10f864
- `MARKER_WALL_FIX_HOST_LOG_BEHIND_GLASS` — 7836a417b7498e8a9337a011d7989a28b233a252
- `STEVEN_LINK_ENFORCE_TWENTY_ENDS_AT_RESET` — 7cc153accf13595b0e2058dda0bb79e437e0efde
- `BREAKER_SELFTEST_FIX_ONE_RED_IN_THIRTEEN` — 9d595a5f47e2ca0611888cf47d5d1481ee79d46e
- `EXPEDITE_GATE_FIX_SPAWNED_ITEMS_LOOK_UNFILED` — 64392a13348f99159ac89df28a825dc4929b0db7
- `OPS_ROOT_GROWER_MEASURE_CAUGHT_WRITING_QMOX` — 7d25cba7fc08e4692ba4f9b4a0f7d4d52759d87c
- `ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE` — 537438a7634fc6d0e884ca1c8c105ca51144cf79
- `STAGE_WAKE_TUNE_NAPS_AFTER_LOAD` — 09828c703d2febdb7c4f82e85347ae0849a8ebe6
- `ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES` — c49e9b53a7cea924f9771070789e18e98d53b026
- `SELFTEST_ALARM_FIX_ESCAPES_INTO_REAL_LOG` — 801e7d68bdf7e3bce0ae99c45bcaebb440d781db
- `LIVE_ROLE_FIX_END_OF_DAY_ALIBI` — c657952845ad3f9c0b5555c698e17fd93c67015d
- `MARKER_DIFF_FIX_EARLIER_WORK_LOOKS_EMPTY` — dfc12e9bfd909d203a4776504679d06efbd8f088
- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_D1A4` — adeb67a4fa7fc1cf469b9fc73b20810abb7e8575
- `BREAKER_ROADS_TEST_FIX_FLAKY_UNDER_LOAD` — ffdbbeb31614ce288fbaa6a0f16c04a5f2563bb7
- `CLONEPOOL_FIX_GAME_WAITERS_HOG_THE_POOL` — e149d7a485a8ec8182062ccf989847a2687ac18f
- `LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART` — aed7de9fc6ff55f4b446677348b6bc2b37c6d303
- `HEALTHCHECK_COMPANION_VERIFY_STALE_DLL` — 78ee182cb4825d607ec58c79897e4c347bf17838
- `LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED` — 73fd40d03127050280668e0ca897c0792ff4a688
- `LIVEPROOF_DOLLAR_FIX_REFUSED_AT_FILING` — ba874a19499bebd1daf6108a0c0cc91cbe5de428
- `PRIORITY_SELFTEST_FIX_BELT_STUB_STALE` — 0eddb2acf7c27d22cb44470265afe8db0636526e
- `WRAPUP_CLAIMS_FIX_ROBOT_BLAMED_ON_WINDOW` — b8bee45dd06077913a7451c97a206be13b9a6dab
- `ARTLEDGER_SELFTEST_FIX_FIXTURE_NEVER_WRITES` — 76797407e3f18b6539836ddc7b268116ecb95ed6
- `RESET_MODE_TEST_FIX_WRONG_WINDOW_WINS` — 5eb7dfe0b368603322d0a6b12831cb915a41ddd8
- `TELEMETRY_INGEST_FIX_CRASH_EATS_BUFFERS` — b956bf93e94743d4184c19709c755e81a0d94709
- `WRAPUP_DEBRIS_FIX_BLAMES_THE_WHOLE_HOUSE` — 5d034a08cfb49c204a51b9cb6d7beed0e21b9181
- `OWNERHOLD_TEST_FIX_UNWRITABLE_STAMP_TAKES` — 2c0919bde5078756175a4e4371eb271cc79eddf5
- `PACING_SELFTEST_FIX_STILL_SEATS_FOUNDRY` — cad9e3ebea93be7f5a3c2340556f041495526254
- `PUSH_REFUSALS_MEASURE_BEFORE_BUYING_GITLAB` — 04aca2dc682a8c355216f5ce184bd7d355d32adc
- `SELFTEST_FIX_EXTRA_ART_COMMISSION_UBZM` — 48e3210f6460b7f52b5b67430e2c6b32d36e9a1c
- `SELFTEST_FIX_FAKEWORLD_PARITY_OTNC` — 9d8ea4211f3fe2eb08a72c34f51557b08399db6b
- `SELFTEST_FIX_SCENARIOS_MAP_JJBZ` — cb5dd12686620fbbe6deca6da79d6ad959622014
- `SELFTEST_FIX_RIMPLACE_JLWJ` — d5c84868f75bdb015128ae1ef502241f603321bc
- `SELFTEST_FIX_SWBESTIARY_PACK_OVERLAYS_MKLQ` — af35b88a13680ba9c201c3c9fe956d221826a309
- `SELFTEST_FIX_RELENTLESS_CODEX_KEEPS_IAAY` — d4247ea94532b78d86b8fc2cbff9b04cd1de6aed
- `RELENTLESS_BREAKER_DIAGNOSE_UNREADABLE_TREE` — 330b67666a160a4e485db91beb8c89abbad6d9e5
- `SELFTEST_FIX_STATIC_CALL_EMPTY_ARG_TEGC` — ecb0c6a0e2213ceffca4042880b0876f5e563c2d
- `LIVECHECK_FIX_JUMPS_THE_GUN` — 32387ec4b07b3dab62a6ad8c5fc56360d78a6738
- `SELFTEST_FIX_FUELSNOWS_NAME_CULL_AAEJ` — f32076b63404fae3a6247666356e152ef397b985
- `SELFTEST_FIX_RELENTLESS_CODEX_FIVE_B_HXGH` — a4c1bbc8dd9e49a1b9cf79b99f531b7efa99db9c
- `STAGING_MENU_FIX_ALWAYS_PARKS_ON_MAPS` — 4ddbe26ec1f90672fba92331819ff2840fca3e12
- `SELFTEST_FIX_TESTQ_FAULT_MONITOR_BOJF` — b251a743366d7b678d10db85c2d8c819cab67085
- `ARTFOLD_LOADFOLDER_FIX_BEETLE_BEHIND_DOOR` — 31385f947fd38e37b81528943d48d8f9e5b7f430
- `GAMEENV_FIX_PROOFSITE_B7C18A7D_ITEMS_WAIT` — ac624392f15be1fdc2308cc2d413eb0fa39ed06e
- `RELENTLESS_REDESIGN_VERDICT_FAIL_CLOSED` — 3d2b3a1cd32d582bf2c2d41aba65121b7c35c9ce
- `GAMEENV_FIX_PROOFSITE_22E336EE_ITEMS_WAIT` — 402dd744209561d4bab0610c82b2b3793b3413c0
- `OPS_STEVE_UNSTICK_UNCLAIMED_ETBS` — 33a577f660fc5ce4c063d5eace1e476af3db875d
- `SELFTEST_FIX_SLIME_SUITE_YTWW` — cf032eae848a2efff99d36b375eb2562b195c680
- `GAMEENV_FIX_PROOFSITE_9E77C59D_ITEMS_WAIT` — 00cc5ed3b416c9e3be416480be5c6b4ebd8956cc
- `GAMEENV_FIX_HARNESS_86430B0B_ITEMS_WAIT` — 704f41feaea883459270268285e09b12669893f3
- `GAMEENV_FIX_PROOFSITE_73C8F2D0_ITEMS_WAIT` — 5f40466c7d745e178253ed562b3352ef9eef9844
- `LAPSED_LEASES_REPAIR_GHOSTS_HOLD_THE_KEYS` — fb720ef7d485883457b15428706af089557fca62
- `PROOFREACH_FIX_PAWNLESS_READ_HAS_NO_WALKER` — 788b39697b4b55b7775ea583c65f360b53504185
- `MODCHECK_ITEMTEXT_RETRY_WSL_HICCUP_FAILS_RUN` — c3fee4051ebf526a86389f8efbf42a6d2c5cf0c7
- `CHECKER_REACH_FIX_OTHER_DARK_SECOND` — c8ed55d3f869484d6f720a9e91319d5f510df206
- `CHECKER_REACH_FIX_STORE_DARK_SECOND` — 1f8eb506e52a97c6e8d69a82a8f49b74e048d60a
- `DEPLOYONLY_SELFTEST_FIX_EXPECTS_UNMEASURED` — f70ad36a4da0
- `CAMERAPLUS_TIER_BUILD_EVERY_LIST_ADDS_RIVAL` — 0eba9dbcc5c7a63b9e5fd2a71fa5f3727cb61fb7
- `CHECKER_REACH_FIX_GIT_DARK_SECOND` — 89067f930e5aca1da34c19057656814350211cb1
- `GAMEENV_FIX_HARNESS_EEE35FD9_ITEMS_WAIT` — b45bac6810a61bd6e3335dca45f95e2b44688a97
- `GAMEENV_FIX_PROOFCALL_B34890F8_ITEMS_WAIT` — 9117436f3f84b8611dcda407e525a29dc342dbbf
- `OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY` — 1bcbaafd7d622d696822e148bee9c13b0bfa36f4
- `CHECKER_REACH_FIX_PROC_DARK_SECOND` — 2407dd04fbdaaa0300f61f512a09bce059dc2a9a
- `DECIDE_MUT_GOLDEN_FIX_TMPDIR_BOUND` — d46c4896cc335c14189a2ce57ed20b12c537840c
- `DEGRADED_PAUSE_FIX_STOPS_ONLY_WHAT_BROKE` — 5963c742c86f98c6e03fb46784c9072462ee3327
- `REDRAW_STALE_SLOT_KEY_AUDIT_DUPES` — e64ba8869ac9d6e8309a01febd4f79d944400a17
- `PRESCREEN_FIX_AUDITS_FILE_SCHEMA` — b7880a8dca09f65c19b12eb3417f914b69d23783
- `READYWAITS_MIGRATE_REMAINING_52_COPIES` — cec3c019908720bcd1f7384b3673259169f54c1b
- `V3_CUTOVER_REVERT_RETIRE_NOW_HARMFUL` — f8f6bf099210afa50d9eea153a7e81c7b2bbe2df
- `COMPANION_DEPLOY_LIVE_ROUND_FORGETS` — fd7422e1dd52f481c170d50bff053e6cddae6ea8
- `NIGHTLY_REDS_FIX_REMAINING_REAL_FAILS` — f3b9929d419c496073a7fb2c884cef08b06397c1
- `CHECKER_REACH_FIX_OTHER_DARK_THIRD` — d937eec4ae55f9c37714d89cef03b31ef261896e
- `GAMEENV_FIX_DEPLOY_590E0C49_ITEMS_WAIT` — 5c18d31cab0fec584d5716d00c40162ded0124e0
- `GAMEENV_FIX_PROOFSITE_18CF717D_ITEMS_WAIT` — 7795dc0bc9e032125a76ee28213155ce4ef4f70b
- `OPS_TMP_DRAIN_RESTORE_DEVU` — 91f784b5e2614e6304a30632401234c73026a200
- `CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK` — 906ba0197f48b543ecaca56bd589d95610de7f2c
- `GAMEENV_FIX_PROOFSITE_7B433874_ITEMS_WAIT` — f3b8ff2c6b98e724a090317f9228298ed79fcb8b
- `GAMEENV_FIX_PROOFSITE_9BC0E9EE_ITEMS_WAIT` — eacf6c7bb718df681bad55bf6636acb6ce4ee772
- `NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK` — 362a7fbb4c21f27dc3ff5f9fb5c85e3c9c6b7b13
- `GAMEENV_FIX_HARNESS_09849AF1_ITEMS_WAIT` — 65fee540593b294d2b8a5dea1ab34068aae80a6d
- `GAMEENV_FIX_PROOFSITE_E94045E9_ITEMS_WAIT` — 0a797678475ee8fef0f00e4231371af463f48433
- `EXAM_SHADOW_FIX_COUNTS_OWN_ECHOES` — 04b4887c84eaa1df37c1e3b3a195492e12f37412
- `FOUNDRY_BACKSTOP_REPAIR_CURSOR_HIDES_INPUT` — 34d410be8eab2a0aa7768507562a44a345d78dfc
- `GAMEENV_FIX_PROOFSITE_0DB67BE7_ITEMS_WAIT` — 46e00ec97386a02166dd2a28e4c838d1cb5b364c
- `GAMEENV_FIX_PROOFSITE_CF15524E_ITEMS_WAIT` — d1578df8f1cf071e41100ee3fa445ad53db83c64
- `GAMEENV_FIX_PROOFSITE_02DE407A_ITEMS_WAIT` — 65b5d40e05d3a8cdf430952b9f806b0dea9521ce
- `GAMEENV_FIX_PROOFSITE_1C77350A_ITEMS_WAIT` — 0698efe57ae0f77251585a08e662ef083eb7e707
- `OPS_CHURN_DIAGNOSE_PLANET_VBIW_HJEC` — 9aeb8b1b3a6603d22335fed56bee35ef23933142
- `CHECKER_REACH_FIX_SEEDS_STILL_DARK` — 7398715b9d47f80dfedd51221431c12e9c50d6f0
- `OPS_SCRATCH_OUTSIDE_CAP_DRAIN_CLCI` — 0b33c89f138aa7d24f4ad73be18b46ed4782b731
- `REAPER_SPIKE_FIX_THREE_STRANGERS_AT_DOOR` — 4c1e59ddbf
- `REAPER_FIX_OWN_SELFTEST_LITTERS_FAKE_SAVES` — 4c1e59ddbf
- `OPS_CHURN_DIAGNOSE_LAPSED_VYPN_VNGX` — 546892f98ed41d6dc05fd77dd42fd9c877d02ad7
- `EXAM_SHADOW_FILL_ITEMS_OLDER_THAN_EXAMS` — 13ad7a51eae8fcd90596827dccda9a658fef6acf
- `GAMEENV_FIX_PROOFSITE_87D091F9_ITEMS_WAIT` — 30de004540bd44139a365470db3258f960270b53
- `GAMEENV_FIX_PROOFSITE_FB127191_ITEMS_WAIT` — abd7949f4b85604fc5ef6795d827dc1814fc7c73
- `GAMEENV_FIX_HARNESS_47EE6093_ITEMS_WAIT` — 8a4e3ac959103ef760aabbe82922bb784163c0fd
- `CHECKER_REACH_FIX_OTHER_STILL_DARK` — 4b1b2b04b3e29ab8692c87f54fc5011d89a6e469
- `OPS_CHURN_DIAGNOSE_ACC_NLLO_VKNQ` — c4beeb3c192c7552e9d8d65d45e1edf21693a3fb
- `REAPER_SELFTEST_FIX_BLIND_IN_EVERY_BOX` — c02e8bcce7d7159e3f29f66bac1d2cd4f366df44
- `GAMEENV_FIX_HARNESS_678B1B18_ITEMS_WAIT` — 7e3b2a9f046220692da212e47d25dd8bfc0c4846
- `GAMEENV_FIX_PROOFSITE_28883863_ITEMS_WAIT` — d7e4b3f52385b8b25ea909786e4d953d80edb00d
- `OPS_CHURN_DIAGNOSE_FOUNDRY_SALI_SUOK` — 8cfea9cadfa5b54dfeef4ecb4432071590a12c1f
- `OPS_CHURN_DIAGNOSE_HEAVY_ZWWY_NYJN` — d87ec72a9095936babc6a37931bcbf471c847839
- `OPS_CHURN_DIAGNOSE_RA_TNDK_QYRZ` — f48153e6fc4d25ef4651b408946a2d27ce755579
- `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ` — 79a4cb66bcb9c016959f6bc075ecbfcf80dce127
- `OPS_TMP_DRAIN_RESTORE_JVCO` — 6f12a2a0d251a71e8f115df75ba7bb272a350bec
- `OPS_HEALTH_WIRE_INSTRUMENT_INCIDENTS` — 552f9d8bd430604b74f274d1347766f1c9414f65
- `OPS_CHURN_DIAGNOSE_NIGHTLY_ZNGK_SBPI` — 8e9bcf22c3c4353ba79278cd10236e76893ed5a8
- `RELENTLESS_EVIDENCE_HARDEN_APPEND_RECOVERY` — 3e1d97efb4c2383b9a03d254816efcff435936b7
- `RELENTLESS_EXAM_HARDEN_SANDBOX_AND_STATE` — b744860bcd4c33179d528c7fddcf38cf3365ada8
- `RELENTLESS_DISPUTE_HARDEN_STATE_MACHINE` — 7065a6fcdaf29657c18ef624eaed246bbc6242d1
- `PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED` — dd19b647186ab97f65262ad7f1151670b0b4000f
- `RELENTLESS_BLOCK_HARDEN_MIGRATION_GATE` — a1b8484f9cf86314c1788dde7ab0bce44069bded
- `RELENTLESS_LIVE_HARDEN_ADMISSION_READING` — 8232f32e9362169c2cf859695aa37c80e5c91755
- `RELENTLESS_BROKER_HARDEN_BRIDGE_CHECK_TOCTOU` — 2514bc638731922ff64ae789c5ed29239a3f0c47
- `RELENTLESS_REWIRE_BACKOFFS_ON_CAUSE_CLOSE` — fd4128bd8b5f62350f5eeb6f1c0d147f10ba041a
- `RELENTLESS_WAKE_PROBE_BOUNDARY_GAP_165S` — c4957be5e35cc9f1215ab4317c00fd7068e9dcdb
- `RELENTLESS_EVIDENCE_HARDEN_GATE_SHADOW` — 5baf796c5773e560a4d635a0b1a0c74dc0366a43
- `EVIDENCE_SHADOW_FIX_REJECTS_EVERY_CLOSE` — 789b5d71a295a614f3dde763048591b9c3eddbad
- `RELENTLESS_WAKE_HARDEN_FAILED_SERVE_ACKS` — 207d1cc22aec4aea32bab546ea2ee76e90ae004d
- `HARNESS_ROWS_FIX_PATTERN_MISSES_CUT_TAILS` — 9289a4731c2501ca9f85c1ff0896b39e0ba3b48c
- `OPS_CHURN_DIAGNOSE_ART_NRXZ_GNMV` — 1532b1c06f8d678c92914d2426bdaf8dc069b35d
- `OPS_CHURN_DIAGNOSE_ART_VURK_JIPJ` — 72f4a6be0508fdba1390486ac1ad5adfca3e7697
- `RELENTLESS_BOXRUN_HARDEN_PARTIAL_PROOF` — 300c7f73c1c00592b37d90ffe8927913ecd01d12
- `RELENTLESS_JOBS_HARDEN_EXIT_WINDOW_RERUN` — bbaae849446d8cf495bf2be01fe430e3a0b2d6ab
- `ART_LEDGER_VET_PURGE_BAN_REVIEW_OWED` — 79f481c3bcd869c91653a08160c90b60ea3b46d6
- `RELENTLESS_FIX_CHECKBOX_TEST_SERIAL_LANE` — f008efd7fb13a7700fa4540f72550c230e10736b
- `SELFTEST_FIX_ALARM_REPEAT_WORSE_WQKI` — c5c75f61f00bd441d52a982ddc916016937273b5
- `SELFTEST_FIX_FALSEPASS_LATE_IPFP` — ba95cc0e748316a45d9d6a0f3d14b6aa9b6e8002
- `SELFTEST_FIX_RELENTLESS_CAUSE_KGEG` — 4cba6b58d348c7fd0f4c7560a1ec4a2ec777f371
- `SELFTEST_FIX_RELENTLESS_CODEX_FIVE_AZEU` — 0c3e2fd71d415a6b692764f4fad45ee1c882f5a3
- `SELFTEST_FIX_BIOME_GROUP_SIZES_IMZR` — 8f20da892f8a1560a08fa07f71dd95738d6f76b4
- `SELFTEST_FIX_HOSE_LAY_SETTLE_ITXN` — d95b15b0bcbf71a66f82c91f41e0ccadf35821ee
- `SELFTEST_FIX_PROOF_PRECONDITIONS_QLXL` — 3e9388e063a8fea0189f2bf4931622b45f0b0375
- `SELFTEST_FIX_STUN_SCALING_NNVH` — 4035d07741273f38411f00fc73a57db06b0fc17c
- `SELFTEST_FIX_DISPATCHER_MUT_YCJR` — 226ed8c7e1fc4f229b651b70aed272542b938711
- `SELFTEST_FIX_ARENA_METER_NRDE` — c5c75f61f00bd441d52a982ddc916016937273b5
- `SELFTEST_FIX_DONOR_OFF_W4_VERDICT_RWUA` — 0ebab1272922ae6212a2539a7b20f3e6d119335f
- `SELFTEST_FIX_REVIEW_MAP_IPJR` — a14cb836f948790fee730d404605ae26d57a3b3a
- `SELFTEST_FIX_STATUS_BOARD_NHHC` — 0ebab1272922ae6212a2539a7b20f3e6d119335f
- `SELFTEST_FIX_TIMER_PRUNE_UPBP` — 37f0ac2fbba5e459aaeaeb23ee7883efc4479bce
- `SELFTEST_FIX_OPS_RANGES_VJAS` — 35a199912f5db85234b1ee40cb4477b1bdc23242
- `SELFTEST_FIX_INCIDENT_ZXZH` — 877862061e6d10b53f16d21c31cd20308a4bf527
- `SELFTEST_FIX_L1_DONOR_OFF_ROUND_GAKJ` — 684c1e2bf92121d70b786d354e9ae39d4f17222b
- `SELFTEST_FIX_ONE_PATH_SEAM_IXBQ` — 9ec2b52cee875c1376c85304e766d5277328dcdb
- `SELFTEST_FIX_PREFLIGHT_CALM_CCNK` — 88e1516d37b50a7abb4e7f390291d83d82f25553
- `SELFTEST_FIX_PYRELANDS_SITE_SDAR` — 6543b740bb0eb5f28bc3a2cba1fc77cf942110d5
- `LIVE_PROOF_LINES_FILL_FOR_BUILT` — 448eaed41399f1e6e10dc27b9c0b796e33f5ae11
- `STEVE_FILLER_MONITOR_FAIL_FINDINGS` — c37d892e976c0a9797306497fa63e28d82c874dc
- `RELAPSE_CHURN_FIX_DIED_TWICE` — 5ba3aa48a71ed8107facf547b4f5e8f3e1b291ba
- `SELFTEST_FIX_DEWBACK_OWNED_CYAQ` — d3e7887c786fc53c1a9692cd506e496de91eaec7
- `SELFTEST_FIX_FLEET_MODS_TTLL` — 2e1f893b28bb35ce33dc13cbc2ff6f88c11e78ba
- `VALIDATOR_BANK_FIX_FAKE_WORLD_NEVER_PROBES` — 6716f4f30262bc37c25eb28e3ebd86c8ed2a28ff
- `RUNNING_BOARD_FIX_FINISHED_JUDGES_CRY_WOLF` — 3c8400f7ab9867bb46c25614c1d697b53d9019d2
- `WILDGROUPSIZE_FIX_TWO_SPELLINGS_ONE_FIELD` — 384d33cecd289245ac8235819493a77fb87d7e5d
- `PROOF_GATE_FIX_CONDUCTOR_MEND_FRAMED` — 78bf4a0ebb5a0799bec1e26d2f9c9e2f988b239b
- `RUNNING_BOARD_FIX_DONE_COUNT_LAGS_PASSES` — 1693cd4f9d3e665a2768c5c41b8eba0e8b17e29a
- `ENACT_SELFTEST_FIX_NO_SCRATCH_IN_BOX` — 2b10273c2bc9e17d705301d8535be942fbc4290d
- `KNOWNREDS_FIX_METRONOME_SHUT_THE_DOOR` — b76c252b8a486caf87903d86842076d6413cf797
- `LIVE_SESSION_FIX_REVIEW_LEFTOVERS_STILL_WARM` — adbec0ac5576f0e0a097310c7045629206e953d2
- `STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION` — c62def14f23bdfef549fb3aa24743a4dc4806b6d
- `TICK_STAMP_FIX_FAKE_FOLDED_WENT_STALE` — 021255da883d8d9be361cca54769518539063753

## Filed and still open (135) — the next seat's queue

- `COLDLOAD_PROVE_DEFLOADCACHE_HALF_INSTALLED` — Trial DefLoadCache (Workshop, RimWorld 1.6, needs Prepatcher: zetrith.prepatcher is already in our Workshop folder 2934420800, DefLoadCache is not) on
- `STAGING_REWIRE_PYTHON_NOT_AN_LLM` — Relentless game staging becomes a Python function, not an LLM session: replace fx.launch(stage_prompt(...)) in src/RimMandrake/rimflow/relentless_game
- `PACING_PRUNE_LLMS_SLOW_ENOUGH_ALONE` — Drop Relentless live-round pacing: in relentless_live_round.py DEFAULTS remove round_max 6 and the 1800 s round_every_s clock (rounds run whenever eli
- `PROOFLINT_WIRE_AT_FILING_NOT_AT_RUN` — Offline proof-line checks at rimflow file/close time, not at the live round: call relentless_live.owed() and refused_proof() (criterion cut at 160 cha
- `UNMEASURED_ROUTES_WIRE_NO_SIX_HOUR_NAPS` — Give each UNMEASURED cause a coded route instead of a 6 h wait: proof exited 2 (229) -> harness fixer with stderr now; not deployed (85) -> deploy and
- `TICKBURST_PROVE_MANY_TICKS_ONE_FRAME` — Experiment: a JawaBench tool that runs N Find.TickManager.DoSingleTick() calls inside one frame with a per-frame wall budget, re-reading ticksGame aft
- `BENCHSHARD_DIAGNOSE_SAME_EVENTS_NEW_ORDER` — Something rewrites infrastructure/state/ledger/events/BENCH.jsonl with the SAME events in a different order (no adds, no losses), leaving it dirty in 
- `WTPROFILE_FIX_TESTS_STILL_ASK_FOUNDRY` — selftest_seat_restart crashes: test_g9_wt_bench_keeps_the_conductor_wake_under_seat_loop and test_wt_profile_wrap_only_when_enabled call install_wt_se
- `LIGHTSPEED_WIRE_GSS_FIRST_NO_LLM_PATH` — Lightspeed, GSS first (spec §3): GimmeSomeSlack in wired_mods.json; an exact-tier tier:gimmesomeslack testq job running northstar/proof_all.py --live 
- `LIGHTSPEED_WIDEN_112_MODS_NEVER_QUEUED` — Lightspeed rollout step 1 (spec §4): 112 mods are testq-selectable but never queued (2,966 modcheck rows). Extend wired_mods.json in coverage.py rank 
- `SKELLICK_BACKWING_REDRAW_SLIVER_VIEW` — Skellick back-view flip-book flaps only slivers: draw a north wing layer
- `ARTEVAL_WIRE_FLYER_MASTER_NOBODY_WRITES_IT` — art_eval runner.flight_layer_rows needs the accepted body master job (record derive_from/master_job) to file wing-layer rows; nothing in art_eval writ
- `ARTEVAL_FIX_WING_LAYERS_SQUAT_BODY_LANE` — art_eval wing-layer rows (runner.flight_layer_rows) inherit the body target_texpath; three poses per facing then bind the body lane on sheets/installe
- `RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL` — Royal Rind against Scald steam is NEAR-IMMUNE (owner by card 2026-11-06): RM_Apparel_RindCoat (and rind garments generally) slow the Scald steam expos
- `CONDPROBES_WIRE_ENGINE_READS` — Bridge conditions T2 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T2; acceptance as written there): Verse IProbeSource f
- `ADVANCEUNTIL_WIRE_PER_TICK_STOP` — Bridge conditions T3 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T3; acceptance as written there): safe_advance stops o
- `CONDWATCH_BUILD_OWNED_RINGS` — Bridge conditions T5 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T5; acceptance as written there): jawa/cond_watch arm/
- `RINGPROBES_WIRE_EVENT_CURSORS` — Bridge conditions T6 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T6; acceptance as written there): ring.count over dama
- `GLASSWALK_MIGRATE_EXACT_EDGES` — Bridge conditions T7 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T7; acceptance as written there): USE ticket (§3): rew
- `POLLLOOPS_MIGRATE_TO_UNTIL` — Bridge conditions T9 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T9; acceptance as written there): lint_calls.py rule f
- `FLYERFRAMES_PROVE_JOINT_SESSION` — Bridge conditions T10 (spec design/RimMandrake/bridge_conditions_2026-11-06/build_spec.md §2 row T10; acceptance as written there): flyer flight recor
- `BATCHREADS_BUILD_ROUND_TRIP_CUT` — Batch read bridge tools in the get_terrain_batch pattern (things-in-rect, pawn-state, fluid-cells, power-nets); round trips cost ~53 ms each. Proved b
- `SHOTSETTLE_BUILD_PAUSED_BARRIER` — Screenshot helper that settles tweened pawn positions (PawnTweener, stale DrawPos after bulk stepping) while paused, advancing no ticks; proved by a t
- `SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY` — Move scenelib.run (src/RimMandrake/Utils/scenes/scenelib.py:44, plays unpaused at speed 4, >=200 ms per call) onto paused _BridgeBase.ticks; judged by
- `STEPCALLS_MIGRATE_WHERE_VERDICTS_HOLD` — Migrate the ~255 remaining direct rimworld/step_game_ticks callers onto safe_advance in batches, each batch adopted only if it passes TICKBURST_PROVE_
- `MURRELITH_FLIGHT_DECIDE_SIX_COATS_ONE_WING` — RM_Murrelith flip-book: 1.6 AlternateGraphic has no flying prefix, so 6 coats share one flight look; pick shared base flip-book or a C# per-coat swap
- `CONDPROBES_WIDEN_HEDIFF_CELL_WEATHER` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): new capability: probes pawn.hediff(def) (has, severity), cell probes taking a pawn reference (cell 
- `RINGPROBES_WIDEN_MESSAGES_RING` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): new capability: a Messages source for the owned-cursor rings, ring.count(messages, ...) stopping an
- `FLOWSTUBS_DRAIN_SIXTEEN_TO_SCRIPTS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): the 16 FlowWorks proof_all stub rows (10 until stops, 2 cell.temp reads, 3 watchers, 1 letter-ring 
- `FLOWWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 15 FlowWorks walk bars into proof lines (5 depth reads, 8 until stops, 2 alarm watchers) (15 units)
- `PMECHWALK_DRAIN_BARS_TO_RINGS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 7 PyrelandsMechanics walk bars (7 units). Done when all its units run on Lightspeed with no LLM and
- `PYREWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 5 Pyrelands walk bars (5 units). Done when all its units run on Lightspeed with no LLM and each ret
- `ATMOWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 5 AtmosphericBase walk bars (glow / fixture colour / claimant samples) (5 units). Done when all its
- `SEASWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 3 SeasWaterline walk bars (3 units). Done when all its units run on Lightspeed with no LLM and each
- `FIREECOWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 2 FireEcology walk bars (2 units). Done when all its units run on Lightspeed with no LLM and each r
- `SCRUBWALK_DRAIN_BARS_TO_WATCHERS` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): 2 LeaningScrub walk bars (2 units). Done when all its units run on Lightspeed with no LLM and each 
- `LIVESTOCKWALK_DRAIN_BAR_TO_WATCHER` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): Livestock bar skarnix_leaves_the_light (1 units). Done when all its units run on Lightspeed with no
- `CUISINEWALK_DRAIN_BAR_TO_UNTIL` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): Cuisine bar cooked_at_campfire (1 units). Done when all its units run on Lightspeed with no LLM and
- `ANTIQWALK_DRAIN_BAR_TO_UNTIL` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): Antiquities bar reader_at_station (1 units). Done when all its units run on Lightspeed with no LLM 
- `GRAFFITIWALK_DRAIN_BAR_TO_UNTIL` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): Graffiti bar mark_actually_appears (1 units). Done when all its units run on Lightspeed with no LLM
- `CAULDRONWALK_DRAIN_BAR_TO_WEATHER` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): Cauldron bar no_rain_or_snow (1 units). Done when all its units run on Lightspeed with no LLM and e
- `SWPATCHWALK_DRAIN_BAR_TO_WEATHER` — Adapt to Lightspeed (no LLM; vet_leftovers.md §3): StarWarsPatches bar desert_sandstorms (1 units). Done when all its units run on Lightspeed with no 
- `LIGHTSPEED_WIDEN_STEVE_TIERS_MISSING_MODS` — Lightspeed rollout #3 (spec §4): per-mod tiers on SteveDesktop carrying the mods its MINIMAL list lacks (sarg.alphaanimals + mlie.starwarsanimalcollec
- `LIGHTSPEED_WIRE_ROWS_JSON_72_SCRIPTS` — Lightspeed rollout #4 (spec §4): the ROWS_JSON contract for the other 72 standalone proof scripts (FlowWorks 26 incl. proof_hose.py, Stillsand 8, Blue
- `LIGHTSPEED_REPAIR_STUBS_TOOLS_EXIST_NOW` — Lightspeed rollout #6 (spec §4, vet_leftovers.md §5.4): the 42 'UNMEASURED: live check owed' stubs say no tool exists for reads the bridge now has (co
- `POLLLOOPS_MIGRATE_THE_OTHER_SEVENTY` — Migrate the remaining advance-read-decide poll loops (AST census 2026-11-06: 75 tick loops, ~57% true polls, plus 82 sleep-and-read loops; draft.md §2
- `ACCOUNTS_RESTORE_STEVE_LINE_AFTER_BIG_WEEK` — At steven's weekly reset (~2026-11-11 13:59 PST) remove ~/.config/systemd/user/account-plan.service.d/week.conf so account-plan.service reads the stan
- `ISSYSTEM_WORDS_FIX_PIPELINE_READ_AS_CONTENT` — is_system reads ~10+ real pipeline items as content (subject words missing from system_words); under the owner pipeline-only pause they are refused
- `CODEX_FIVE_SELFTEST_FIX_SAVED_PATCH_RED` — selftest_relentless_codex_five #16 red at HEAD 8cf9344f57 and its parent: 'every saved patch is the raw bytes (--no-textconv --no-ext-diff): 0 without
- `LIVECHECK_FIX_TYPEERROR_BLINDS_EVERY_LINE` — The Relentless supervisor's live_check reader raises a TypeError, so every 'live' promise line in recent checks read COULD NOT READ (seen on OPS_JAM, 
- `RELENTLESS_TICK_MEASURE_OUTLASTS_ITS_NAP` — The Relentless supervisor tick takes 5-10 min of work (last 12 ticks: 4.9-10.1 min, journal 2026-11-06) before the 2-min OnUnitInactiveSec gap, so eve
- `PROOFLINES_FILL_857_NAME_NO_SUITE_ROW` — 857 of 882 owed Relentless live criteria still have no live-proof line after LIGHTSPEED_WIRE_PROOF_LINES_882_OWED. Counts per mod are in infrastructur
- `TICKSLOW_REWIRE_CLONES_OFF_THE_BELT` — Cut the Relentless supervisor tick to seconds by moving its slow inline calls off the tick: scratch_clone clone/reuse (fetch, read-tree, checkout-inde
- `RELWAITS_PRUNE_PAUSES_WITH_NO_REASON` — Each PACING row in design/RimMandrake/relentless_fixed_waits_2026-11-06.md that its code gives no reason for (unmeasured_retry_s 6 h, harness_retry_s,
- `ART_XDELETE_FIX_UNLINK_BEFORE_RECEIPT_TOO` — artledger.x_delete unlinks game slots and store bytes before flushing its live/release/purge events (ban is flushed first); a crash between loses the 
- `ART_SELFTEST_FIX_LEDGERFIXES_MISSING_SHARD` — selftest_art_ledger_fixes.py CRASHes on HEAD: its fixture runs git add infrastructure/state/art/events/BUILD.jsonl, a path that does not exist (pathsp
- `PYRELANDS_SCENES_BUILD_EIGHT_JUDGE_GAPS` — Pyrelands proof scenes: entry points furnace_thermal_bed, furnace_herd_migrates; promote firefoam_sprayer, sand_shovel, rite_hook_alone to acceptance 
- `PYRELANDS_TEXT_FIX_ENGINEERED_NEVER_SAID` — Pyrelands BiomeDef description: say the savanna was genetically engineered (leaf biome_text_says_engineered, his root correction)
- `TRACE_MKDIR_HARDEN_STAT_OUTLIVES_IT` — known_results.py: the shim does not note mkdir/mkdirat as W, so os.makedirs(p) (stat p absent, then mkdir p) records p as a dir probe it created itsel
- `BUILDERWALL_BUILD_EXAM_KEYS_SHUT` — Add an enforced walls.builder profile on the real worker launch path that denies the seed keys (RM_SEEDS_PRIVATE) and the relentless store; relentless
- `JUDGEGATE_SHRINK_CLOSURE_IS_118_FILES` — Move the Judge gate (checker_prompt, verdict intake, finish gate) out of relentless.py into a module with a narrow import set, so the self-build prote
- `HACKWATCH_BUILD_NEVER_TUNED_AGAINST` — A hack-watch unit reads each self-build candidate's transcript and diff to tests/oracles/fixtures and their imports; a flag holds the candidate and co
- `SELFBUILD_REWIRE_REPORT_ONLY_FIRST` — Supervisor runs relentless_selfbuild.py protected and promote on a self-build candidate branch, report-only first, then refusing; blocked until BUILDE
- `FLYERPIN_FIX_DERIVED_ONE_AHEAD_OF_PIN` — selftest_donor_off_w4_verdict and selftest_l1_donor_off_round FAIL: 'flyers: derived 25, pin expects 24 (re-pin after a port)'; l1 also fails 'donor r
- `GAMEENV_FIX_PROOFSITE_528224CB_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: the proof exited 2: it did not measure: UNMEASURED: bridge: 'ticks
- `AGENT_IMPROVE_HARDEN_NOISE_CALLED_OVERFIT` — Generalization verdict has no noise floor: first real run called a one-line path fix overfit at 2-3-1 on noise
- `AGENT_IMPROVE_WIRE_GENCHECK_HAND_RUN_ONLY` — Generalization check runs by hand and as the L2 gate only: cadence, revert enactment and narrow-count digest owed
- `TELEMETRY_RESETS_HARDEN_REGROWN_FILE_UNSEEN` — telemetry ingest.py Tailer.pass_source: a reset is detected only when size < cursor; a same-inode file truncated and then regrown past the old cursor 
- `TAILSTATE_SHRINK_WHEN_SPOOL_FULL_BLOATS` — telemetry ingest.py Tailer.commit_durable writes vm.points into kv tail_state on every pass with rows; with VM down AND the 2 GB spool refusing, that 
- `RESTARTREQ_GUARD_RENAME_NO_HARDLINK_RACE` — seat_restart.consume_request: when os.link is unsupported, the exists-then-rename fallback can overwrite a request written between the two calls (GPT 
- `HOSE_STYLES_FIX_RELOAD_DRIFT_SEEN` — FlowWorks SL3_hoses_and_reel_styles_survive FAILs live: hosesEqual False, reelStylesEqual False after save/load (21 hoses)
- `GAMEENV_FIX_PROOFSITE_102FDD57_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: proof exited 2: it did not measure: UNMEASURED: no generated RM_Lo
- `DDRIVE_NVME_REPAIR_RESEAT_NEXT_SITTING` — Archmagi D: NVMe (Kingston SFYRD4000G, root port 0:6.3) throws WHEA-17 corrected PCIe AER, 3-17/day since 10-26 (ops_watch disk.whea_corrected_24h now
- `SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT` — Rename the allocator's FOUNDRY seat key (slot_allocator split/SEAT_NAMES, slot_rules seats/enforce_seats/fallback_n/FOUNDRY_share, helper_budget publi
- `DEWBACK_PIN_FIX_NORTH_REDRAWN_UNDER_IT` — src/RimStarWars/SWBestiary/selftest_dewback_owned.py fails 2 rows: Dewback_north.png no longer matches the pinned set-C sha256 (MAD 255), after 040e27
- `PIPELINE_REDESIGN_START_THREE_AM` — Start the pipeline redesign run at 03:00 PST (D:\ClaudeWork\rimmandrake\conductor\redesign_2026-11-06\PLAN.md)
- `STORE_BLOCKS_RECONCILE_LEDGER_FREED_THEM` — Relentless store keeps JAM_CLASS, NIGHTLY_COP_AQJSGV, OPS_TMP_DEVU, PROOF_HARNESS_SAVELOAD blocked after the ledger unblocked them (~10 dependents stu
- `RETIRED_UNITS_PRUNE_PULSE_STILL_TICKING` — Retired machinery still live: RimPulse pulse timers and pulse-deploy clone still run; stale FOUNDRY references in agent files/CLAUDE.md; units that ru
- `PROOFDROWN_FIX_NATURAL_WATER_READS_ZERO` — RM_PitFillEffects.ProofDrown reads ex.WaterMetresAt (dug cells only) so it reports water=0.00 on natural brine where the RM_Swim tick reads RM_SwimWat
- `GAMEPHASE_UNBLOCK_HELD_GAME_SITS_IDLE` — Items wait on a game phase another item holds while the game does nothing: 246 of 450 item-hours of game wait on 2026-11-03 and 455 of 779 on 11-05..0
- `MODSWAP_FIX_REORDERED_LIST_READS_FOREIGN` — modset_builder.take_before_copy refuses every tier swap when the live ModsConfig holds the before-copy's exact active-mod set merely reordered (md5 di
- `GAMEENV_FIX_PROOFSITE_1CD219EC_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: ems": ["running list has mod(s) beyond tier fw_gss_sitting ['mandr
- `STEVE_MODSCONFIG_REPAIR_CRASH_RESETS_LIST` — SteveDesktop: a cold-load crash makes RimWorld reset live ModsConfig to Core+DLC (seen 04:38 PST 11-06 after canary 618fb0); take_before_copy then ref
- `LIVEVERDICT_REBUILD_ALLOWLIST_MEETS_OPENLANE` — Live verdict rules 1-5 (identity binding, fail closed, proof allowlist, child reaping, keyed fakes + mutants) for relentless_live.py; settle the 2-too
- `ALARMSTEPS_TEST_FIX_ARENA_LEFT_A_GHOST` — selftest_alarm_repeat_worse fails on origin/main 786a7001: STATED_STEPS still lists arena.push_refused_24h, whose rule 1f0e666566 (arena removal) dele
- `CHECKER_REACH_FIX_GH_DARK_SECOND` — Successor of CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS, which closed while the gh reach probe still fails for JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS and
- `BRIDGE_RECONCILE_WIRE_CLOSED_NOT_CURED` — Live proofs still die on rimbridge_client IndeterminateError ('earlier mutating call(s) have an UNKNOWN outcome'): 9 of the last 40 Relentless live ru
- `DRIVERSITE_FIX_HIVE_HALTS_TWO_MAPS` — northstar_driver never clears hostile hives; a mid-chain Hive halts Cauldron water and Forge voices bars
- `REPLAY_BANK_STALE_BUILD_RED_AT_HEAD` — selftest_validator_mutants red on an unmutated bank at 0d00d9543c: STALE_BUILD outcome is NOT_ADMITTED, the bank expects UNMEASURED (validator_replay.
- `SITECALM_FIX_HIVE_APPEARS_MIDRUN` — Live site: a geneline Hive appears mid-advance and aborts bar chains
- `DEPLOYONLY_TEST_FIX_STILL_WANTS_UNMEASURED` — selftest_relentless_deploy_only.py red at HEAD: 4 checks still expect UNMEASURED where ab77ccbdd6 made pre-bridge gaps NOT_ADMITTED
- `GAMEENV_FIX_PROOFSITE_85A85B3D_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: rvived': 1, 'lostToLaterOps': 0, 'failedCount': 0, 'failed': [], '
- `RELENTLESS_ROLE_LAUNCH_HARDEN_CAUSE_BOOK` — role_launch.py WP-15: unlocked cause-book load/attach/save loses concurrent updates; stage_close exception after status flip abandons harvest; Setter 
- `LIVETIER_PREFLIGHT_FIX_TRIPS_OWN_GUARD` — relentless live tier: its own python.exe rimbridge/ping (relentless_live.py ~L1370) and jawa/running_mods preflights end <10 s before the proof, and b
- `RELENTLESS_ENFORCE_BOXRUN_EXAM_DISPUTE` — Flip boxrun, exam, dispute from shadow to enforce
- `RIMFLOW_DELETE_CLOSE_GUARDS_ONE_PER_LANDING` — Delete old close guards one per landing (WP-09c)
- `RELENTLESS_WIRE_MARKER_VERDICT_AND_REPAIR` — Wire Marker verdict append and evidence-index repair
- `RIMFLOW_SYNC_STORE_LEDGER_DIFF_NIGHTLY` — Schedule store/ledger diff, refuse kind=other lift, clear stale blocks
- `RELENTLESS_REMEASURE_TICK_P95_DETACH_NEXT` — Re-measure tick p95 over 100 ticks, detach next slow phases
- `RELENTLESS_VET_FULL_FILE_BEFORE_CLEAN` — Full-file code review of relentless.py
- `HOOKS_MERGE_ONE_DISPATCHER_PER_TOOL` — Merge hooks to one dispatcher per tool (deferred WP-13)
- `RIMFLOW_RETIRE_DEAD_MODULES` — Retire dead rimflow modules, keep close_audit (deferred WP-14)
- `LIVELANE_PROBE_SECOND_GAME_INSTANCE` — Probe a second game instance for the live lane (deferred WP-16)
- `GAMEENV_FIX_PROOFSITE_54339AD0_ITEMS_WAIT` — Game-lane environment cause (proof_or_site) no lane step can fix stops live proofs: the proof exited 2: it did not measure: NO VERDICT: FileNotFoundEr
- `AUDITOR_IMPORTS_VET_PIL_THEN_LXML_MISSING` — Auditor rule candidate: a validation script that imports a third-party package (PIL, lxml) with no UNMEASURED fallback FAILs on the SteveDesktop runne
- `PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES` — Proof cost ledger + live-throughput benchmark (fast-testing #8)
- `LIVE_STAGING_BUILD_STAGEHAND_WITHOUT_TOKENS` — Deterministic Python staging: deploy/restart without an LLM (fast-testing #2)
- `SAMPLE_FILLING_FIX_FOUR_WAKES_PER_CLOCK` — sample_filling waits re-launch a worker every ~3 h instead of sleeping to the stated window end
- `REAPER_DAYPROOF_FIX_READS_SANITY_MIDRUN` — prove_scratch_reap_refused_day.py reads sanity.json while a reap run is mid-write and reports RED
- `OPSROLE_FIX_BUDGET_OVERRUN_REPEATS` — Operations role runs keep overrunning their advisory budget: rm-role-operations-1793978026 used 1077640 weighted (raw 6980334) vs 700000; Dispatcher f
- `PROVEGRAVSHIP_FIX_PIPES_FOR_ABSENT_VGE` — prove_gravship.py setup lays VGE_AstrofuelPipe, a Vanilla Gravship Expanded def; the relentless live game loads no VGE, so the pipe build fails and ev
- `PYRE_WORLDSWITCH_DECIDE_ON_BY_DEFAULT` — Pyrelands ships biomeGenerationEnabled default ON (lets vanilla place RM_FE_Pyrelands on newly generated worlds); weigh against the 2026-08-18 ruling 
- `REBIND_FIX_OFFBOX_CAP_FULL_HOUSE` — Rebind cannot add an offbox adapter to a contract that already names 4: drops() refuses removing any, OFFBOX_MAX=4 refuses a 5th
- `PYRELANDS_SCENES_BUILD_VENOM_GIANT_DUST_DOME` — Pyrelands proof scenes: new flamefang_venom (bite applies RM_FlamefangVenom; control non-venomous bite); ullai_and_giant live RM_FurnaceBeast body-siz
- `PROOFCOST_VERIFY_FIRST_DAY_SLIPPED_BASELINE` — After 24 h of live/proof_cost.jsonl (landed 49ddd0eab189), compare proof_cost.py throughput --hours 24 with throughput --source runs over the same win
- `STAGER_SNAG_REWIRE_BUILDER_WOKEN_FOR_HARNESS` — A game_stage snag (python stager stopped before any proof ran) goes through relentless_game._back -> sup.fail, a strike and a fresh builder gen, thoug
- `BOXTOOLS_HARDEN_IMPORTS_PLANTED_CV2` — evidence.box_tools probes run '<py> -c import cv2, numpy' with the caller's cwd and no -I: a checkout-controlled cv2.py in cwd executes on the supervi
- `EXAM_OWNER_CLAUSE_HARDEN_TRUE_PASSES` — relentless_exam: lint accepts kind live/owner and validate/run_exam skip them, so an exam of only an owner clause with argv [true] validates with no r
- `WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES` — Every wrecked tier draws in pipes and conduit like its repaired tiers (RM_PumpingStation_Wrecked first)
- `INCIDENT_FIX_BROKER_FAULT_ROUTELESS` — selftest_incident red at origin/main 3e1d97efb4: alarm kind broker_fault (relentless_broker.py:132) is missing from the incident routing table
- `GIT_DARK_FIX_STALL_ITEM_STILL_HELD` — False close: BRIDGE_STALL_DIAGNOSTIC_1 is still held on git reach after CHECKER_REACH_FIX_GIT_DARK_SECOND closed
- `EXAM_SETTER_FIX_DEMANDS_ITS_OWN_MECHANISM` — Exam Setter tests one mechanism it chose, not the item's outcome: 16 of 18 shadow reds wrong
- `EVIDENCE_HEAD_SEAL_REPAIR_THREE_BEHIND` — evidence store index does not verify: HEAD names 143 index rows ending 4c7c8fb58e, the index has 146 ending 38b1157978; every boxrun receipt refused (
- `CAUSE_SELFTEST_FIX_C7_ROUTES_NOWHERE` — selftest_relentless_cause.py C7 rows fail on HEAD 68355c56a1 (not_measuring/blocked_here route to no fixer)
- `RIMFLOW_BUILD_ONE_EVIDENCE_RECORD` — Evidence predicate in cli.py close gate, shadow (redesign 09b)
- `MAKEBOX_REWIRE_OFF_TICK_STILL_TOP_LEAF` — Detach relentless_wall.make_box (checker box build) off the tick
- `NULSCAN_REWIRE_OFF_TICK_GREW_SINCE` — Detach relentless_integrity.clone_damage NUL scan off the tick
- `CLONEBYTES_REWIRE_OFF_TICK_NEW_THIRD` — Detach scratch_clone.clone_bytes walk in pool_load off the tick
- `LEASEPREP_REWIRE_OFF_TICK_SIX_MINUTES` — Detach relentless.prepare under _lease off the tick
- `CLEANCHECKOUT_REWIRE_OFF_TICK_CLONE_INLINE` — Detach relentless._detached_clone in clean_checkout off the tick
- `LEDGERCLOSE_REWIRE_OFF_TICK_ONE_PROC_EACH` — Batch or detach relentless.ledger_close rimflow calls
- `RELENTLESS_REVIEW_FIX_ROUND_SIX_STILL_DIGS` — Codex r6 full-file review of relentless.py: 22 unverified findings (symlink restore, give_back over a hold, string pause prefixes, ...)
- `TMPREAP_PRUNE_OVERCAP_COPY_STUCK_40_HOURS` — scratch_reap refuses a /tmp git copy whose untracked tree is over the 2 GB preserve cap, forever
- `CONFIGERRORS_FIX_THREE_LEFTOVER_CLASSES` — Config errors left on every full-list load after the wildGroupSize fix (384d33cecd): duplicate thingCategory on RM_AncientStasisLocker_*, RSW_RakatanS
- `SHEETSAID_DECIDE_769_TAGS_HE_NEVER_TYPED` — Art ledger: ~769 owner events hold agent sheet-pick tags in said ('reject+purge on sheet <stem>', '(sheet decisions)', '✕ on the facings needs-eyes sh

## Commits

```
be8030cf58 art_eval auto-judge pass 20261106_0951: audit_auto_20261106_0951 (4 decision(s), 6 installed file(s)) (ARTEVAL_FINISHED_RENDERS_WIRE_AUTO_JUDGE)
eac80f965d conversations: catch-up 63 record(s)
b47c87d04b CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES: drop verdicts/tiers replay families, export+schemas, arbiter_pending.py
e381b38da8 ARTLEDGER_SELFTEST_FIX_WRONG_SHARD_NAMETAG: clean mark for selftest_art_ledger_fixes.py
ff72d43fc6 ARTLEDGER_SELFTEST_FIX_WRONG_SHARD_NAMETAG: test_a takes its shard from artledger.seat()
b0cb662ef3 ledger: ops_watch alarm(s) note:NIGHTLY_RED:testing.red_yifdea
1ab527ed99 ledger: relentless supervisor
6a39559ddb ledger: relentless supervisor
ccc823d12d ledger: relentless supervisor
1c4b444e72 CARD_PARAPHRASE_AUDIT_SAID_IN_DISGUISE: lesson, boxrun reads hyphenated subcommands as prose
ae60d45aa7 CARD_PARAPHRASE_AUDIT_SAID_IN_DISGUISE: art.py card_said alias (the box parser reads a hyphenated subcommand as prose)
5b08aaea68 CARD_PARAPHRASE_AUDIT_SAID_IN_DISGUISE: file SHEETSAID_DECIDE_769_TAGS_HE_NEVER_TYPED
c9752e90b1 CARD_PARAPHRASE_AUDIT_SAID_IN_DISGUISE: card-said also matches bare card option labels; 20 more owner events said -> by_card
adbec0ac55 LIVE_SESSION_FIX_REVIEW_LEFTOVERS_STILL_WARM: B4 voids a stopped block's criteria; quote verify evidence path
c1f43617f2 HARNESS_REPAIR_CAUSE_C1B99C19: re-run pointer -> c68996 (e22349 was INVALID/DEPLOY, stale companion)
8ea32b5a63 HARNESS_REPAIR_CAUSE_C1B99C19: file HOSE_STYLES_FIX_RELOAD_DRIFT_SEEN (SL3 FAIL in re-run b4fe4d)
c62def14f2 STAGING_REMOVAL_FIX_ONLY_KNOWS_ADDITION: staging takes live-without mods off the list (modlist_swap --disable)
4235cf7327 ledger: relentless supervisor
b76c252b8a ENGINE_REVIEW_FIX_LEFTOVERS_STILL_WARM: fix Codex cd905b leftovers in relentless_game/live and modset_builder
46e62607ab ledger: ops_watch alarm(s) note:NIGHTLY_RED:testing.red_xonoch
... 1219 more: git log --oneline 4292fd4e5a..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     relentless staging PROOF_COST_MEASURE_BEFORE_THE_ESTIMATES: deploy and restart for its live proofs

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M Transient/biome_ffar/scale_ground_measured.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art/events/BENCH.jsonl   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Chellow.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Gembug.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Krissek.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Lirrith.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_TheUnfinished.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Wuum.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Ysvaltha.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/RM_Zrrik.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/art_eval/briefs/SWPotF_RaceDef_ysalamir.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/code_review/BENCH.jsonl   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/ledger/events/BENCH.jsonl   mine: committed with this handoff
 M infrastructure/state/ledger/events/OWNER.jsonl   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M infrastructure/state/ledger/events/RUNNER.jsonl   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? cards.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? deployed/config/ModsConfig.before-tier-weepingstones_solo.xml   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? design/RimMandrake/designer_drawing_out.md   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? design/concepts/Pyrelands/coverage_verdict.json   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? infrastructure/state/lessons/20261105T024235Z-CONDUCTOR-tmp-full-alarm-2026-11-05.md   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
?? shortcuts.ps1.txt   peer seat/helper (Relentless, Designer, art-eval, RUNNER); not this window's, left as found
```

