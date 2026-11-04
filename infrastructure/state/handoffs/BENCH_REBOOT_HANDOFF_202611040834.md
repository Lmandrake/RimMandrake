# BENCH_REBOOT_HANDOFF_202611040834 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611032232`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
Relentless read broken tests, harnesses, unreachable evidence and wrong contracts as broken WORK and rebuilt good code in loops: Operations' first reading on its new churn SLI (07:52Z) was 59 items in churn, 72% of Relentless tokens on returned work, 17.5% of live runs measuring anything. Tonight's fixes: Marker UNMEASURED (651a027cfb), narrow WEAK live (ede0dff499, owner by card), proof paths widened (296038a63e), live classifier + diagnose-first + `snag --class instrument` (80b30b1bd5), attribution gate + instrument incidents enforced in the supervisor (52277abce1, GPT round 3 SOUND), Operations churn SLIs (d281d6261d). The owner's ruling is in standing_rulings.md ("Broken tests are expected"); GPT's plan is design/RimMandrake/test_tolerance_gpt_advice_2026-11-04.md. WATCH the churn SLI fall over the next day; if it does not, the gate is leaking.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- The churn numbers above are the pre-fix baseline; tell him the next reading (relentless churn SLI in /mnt/d/ClaudeWork/rimmandrake/ops_watch/health.json, incident OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV).
- 29 items were sent back for recheck at once tonight (24 GAP:OTHER WEAK holds + 5 proof_rework holds). GPT warns the narrow-WEAK change moves ~25% of verdicts: the first false-close audit (CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY) must sample those closes.
- SteveDesktop lane runs again (849cbd013f etc.) but its FlowWorks site holds a dead colonist, so fillers measure little until HARNESS_REPAIR_CAUSE_E0B6DA41 lands (expedited).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG` — Relentless store done gen 3, ledger still doing; NEXT: run `rimflow show ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG` and close it on Relentless's sha if the belt left it open
- `BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE` — Relentless game phase gen 6 (released from a GAP:OTHER hold tonight); NEXT: leave to Relentless; check `relentless.py show` next wake
- `BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING` — Relentless checking gen 1; NEXT: leave to Relentless
- `CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY` — filed tonight from GPT advice rank 6, expedited; Relentless reads it blocked gen 1; NEXT: read its block reason with `relentless.py show` and unblock or route it
- `CONDUCTOR_RESET_FIX_KILLED_MID_READ` — queued gen 7, released from a GAP:OTHER hold to recheck; NEXT: confirm it rechecked rather than re-staffed
- `HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS` — Relentless candidate gen 1; NEXT: leave to Relentless
- `INCIDENT_REVISIT_TAME_SAME_NEWS_HOURLY` — queued gen 9, released from a GAP:OTHER hold; NEXT: confirm it rechecked rather than re-staffed
- `JAWABENCH_TPSARCHIVE_FIX_SKIPPED_AFTER_FAULT` — Relentless store done gen 5, ledger still doing; NEXT: close the ledger item on Relentless's sha if the belt left it open
- `JAWABENCH_TPSSTARTUP_HARDEN_REMAINING_BG_JIT` — ledger built, Relentless blocked gen 4; NEXT: read its block with `relentless.py show` and route it
- `NIGHTLY_SELFTESTS_DRAIN_THIRTEEN_RED_NIGHTS` — queued gen 4; nightly sweep was 57 FAIL of 1018 on 11-03; NEXT: read the 11-04 03:00 nightly result and re-judge incident testing-20261101162433
- `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE` — Relentless checking gen 1; NEXT: leave to Relentless
- `RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM` — Relentless candidate gen 9; NEXT: leave to Relentless; if it returns again, read its attribution
- `RUNNING_PAGE_BUILD_TOKEN_FUEL_GAUGE` — queued gen 5, released from a GAP:OTHER hold; NEXT: confirm it rechecked rather than re-staffed
- `SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL` — Relentless candidate gen 1; NEXT: leave to Relentless
- `STATUS_PAGES_BUILD_REPLACE_RIMPULSE` — Relentless held gen 3; NEXT: read the hold reason and triage it (an 'owner:' hold is usually not his)
- `STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO` — Relentless queued gen 2; NEXT: leave to Relentless
- `STEVE_LANE_MONITOR_PAUSE_FINDINGS` — Relentless retired gen 2, ledger ready; NEXT: decide: drop it or re-enrol it with `relentless.py reenrol`

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A relayed --owner-said claim/start stamps the item OWNER and locked the Conductor out of verify/close; fixed 18bd62d359 (filed: infrastructure/state/lessons/20261104T054048Z-BENCH-relayed-owner-said-claim-start-stamps.md)
- Operations counted 'returned'/'blind_fail' as belt progress, so churn read as health; fixed d281d6261d (see: OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS)
- `git reset --mixed origin/main` on a clone that was behind left the working tree reverting 47 upstream files; restore each with `git checkout origin/main -- <path>` (see: clone-landing-commits skill; prefer ./sync after landing the stray commit)
- The testq steward dropped a Steve repair item as 'recovered by itself' while a helper was fixing it (filed: infrastructure/state/lessons/20261104T081823Z-BENCH-steward-drop-misattributes-repair.md)

## Closed since the last handoff (108)

- `NIGHTLY_COP_FIX_RED_ADEAUS_MRKD` — 29a1da22aca17fb3fd91dfcd162b88b191c644c4
- `NIGHTLY_COP_FIX_RED_AYQENC_HIKO` — 3f9f0b02263e2bff8c7a8273b2e19c5ba5297de7
- `NIGHTLY_COP_FIX_RED_CZZSPJ_OFFZ` — da62c32731adc33cc264265e31846a57a044f1e4
- `NIGHTLY_COP_FIX_RED_ATJKEB_FBYD` — 60758238a0d2301e33f92a5a4fac159304dc31a8
- `NIGHTLY_COP_FIX_RED_CYGHVG_QCWJ` — 784626a0ad715082344f011da7abecd934c737c5
- `HARNESS_OOM_MEASURE_NINETEEN_QUIET_KILLS` — eb31958c12de38a108234728ef466cb80c6026c4
- `HARNESS_OOM_MEASURE_NINETEEN_QUIET_KILLS` — eb31958c12de38a108234728ef466cb80c6026c4
- `STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE` — 715b7281f01c327a68cd207a0ae52c6a57506929
- `STEVE_BRAKE_FIX_KNOWN_CAUSES_RELEASE` — 715b7281f01c327a68cd207a0ae52c6a57506929
- `NIGHTLY_COP_FIX_RED_BXSKPY_FGXD` — b52e86557476afe985d7483bba2acc0e309fddcc
- `RELENTLESS_SEAT_UNTANGLE_FROM_BENCH` — 7cd6f4e2a75b83c7abf9077e04db7bd7eb333bdd
- `NIGHTLY_COP_FIX_RED_INLFTF_XEWJ` — 6591134db91a70d4d340a624c18c6b6b12ad8990
- `COMPANION_STAGE_FIX_JOBS_ARRIVE_STALE` — 9cc33ce7a663e36ec68b80ff3b1a2d74ce052ba5
- `NIGHTLY_COP_FIX_RED_FPVNUY_IBXW` — 4b41f25c1193856256e2001978c6ed6061c57c75
- `NIGHTLY_COP_FIX_RED_LUENJV_OOHG` — d8c7aca6a64023cc9c29097e0e52364dcac13d46
- `PROOF_RERUNS_TAME_UNMEASURED_REPEATS` — 8493554c0e4677d306ed752a669a05f4097a3632
- `NIGHTLY_COP_FIX_RED_EQDNFF_XKUH` — 1d62ce35b2240f3bb9f1df750bdace274e6f6a70
- `NIGHTLY_COP_FIX_RED_HMGHDI_RQAA` — 14a2ab94964785da129b24de786780e30e894218
- `NIGHTLY_COP_FIX_RED_NZZZPC_NAFD` — a0538b1356542f74139543e6f4c621ecf81ba021
- `NIGHTLY_COP_FIX_RED_TKFRGB_FSIQ` — 02e95607d22e18ab2f3073da7720df76bc91c2b3
- `NIGHTLY_COP_FIX_RED_UPIXSC_QQDI` — 61c7fa8bd93d4fe9b60d45c2b8fd867ed61a1136
- `NIGHTLY_COP_FIX_RED_TUOOLR_EGFR` — c01c4881926e6d94fccd570bce514d079f27a6a3
- `RELENTLESS_TICK_TUNE_FIFTEEN_MINUTE_NAPS` — 850b23c1b1376d6273926b984856ac0ff9952252
- `NIGHTLY_COP_FIX_RED_MPLZPJ_VKOU` — b44282693fd1819d9b70575d4b9c488d05589232
- `RELENTLESS_FIX_PARKED_ITEM_STILL_STAFFED` — 44ac6b03f071749088bd3c9b20c40c7b65338e2e
- `RELENTLESS_GAME_FIX_HOLD_LIFT_FORGETS_GAME` — 477aa5f6261fdb257516c71ea697c6bc820fe4ac
- `RELENTLESS_DEPLOY_WIRE_NOBODY_MAY_APPLY` — 7df07616108ca9fef7f07eb4364968da286f622d
- `RELENTLESS_START_SILENCE_REFUSED_RETRY_LOOP` — ddcd6ca8c9cd2571cdf58ba3052500f218b85a50
- `NIGHTLY_SWEEP_HARDEN_DIED_AT_SIXTY` — 0b0972d84ddd71639ff3dd093b3e7d574ea78700
- `POOL_STRANDED_FIX_LANDED_COMMITS_STILL_HOWL` — 17e0afbc9124e8a36c5d7732bf011d2bfccd1104
- `ALARM_CENSUS_EXTEND_BUILT_NAMES_SLIP_PAST` — e9eb77260508454bc88a27c266b1db18f01d6cd9
- `RELENTLESS_STRIKES_FIX_EMPTY_ACCOUNT_BLAMED` — 133f6e67b922a960245a7bdad515a43faebc9276
- `REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN` — b0fb6fe124d7dec511ceedeb4447e0c81a7aff92
- `RUNNING_PAGE_BUILD_WHOSE_TANK_IS_THIS` — d1410b5763c0
- `ALARM_REPEAT_FIX_BREAK_ON_WORSE` — 547224ce018c34552a7fb12573090db6e84d1da0
- `RELENTLESS_HOLD_FIX_TOOLING_ISNT_OWNERS` — 04e3621fbcd6e0dbbae6436d4694830e8fc21dd1
- `STEVE_FAULT_MONITOR_ONSET_BEFORE_RESULTS` — 5aad64f5cddf410447deb3540a3c6c328c6f7a2d
- `OPS_ALARM_FIX_LOG_LINE_NEVER_RETRIED` — 1aa587e388aa72b2bad58b90802211aae4d82774
- `OPS_RANGES_FIXTURE_REPAIR_FOUR_CLASSES_SHORT` — b275106d69a48b9527f671e8d34cb14849397e3d
- `OPS_REFUSAL_REWIRE_TO_CONDUCTOR` — b105e9a9c985ccbbd80c0525cfa359bbab198c2c
- `RUNNING_PAGE_BUILD_NAMES_ON_THE_BELT` — 1c42baedfd0ab1ab131bc774316625d7f29f35df
- `POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG` — 7684d1bcbed34a078dd2639054a48af2cf5d52fa
- `OPS_NIGHT_GAP_FILL_COVERED_SLOT` — df1905475c9e774710524b09e7a1aef9aebe02c6
- `RUNNING_PAGE_FIX_REVIEW_LEFTOVERS` — 56d0b295be47bbff9e3e6519778e19ecc11dce04
- `OPS_RAISE_REWIRE_WITH_DEATH_LADDER` — 643aa0b5579f53730ee2c0cb7ea456335856e552
- `OPS_CLOCKS_DEPLOY_ONE_PINNED_COPY` — 0f3e9fcd6fbb14d669a6b93ed21ffb83f0a0438c
- `OPS_METRONOME_PROVE_IN_SHADOW` — 306e8f56e12c918b07c710a3c4874052bc6a326b
- `OPS_OVERSPEND_FIX_ALARM_FEEDS_ITS_METER` — fc59e15f9da1515dc45932f688d31c390512a397
- `OPS_ROLE_SHRINK_RUN_COST` — 85260ec4eb9c488024e2260dd10c99fef56109f3
- `OPS_JUDGE_NOTES_MEASURE_VS_NO_CHANGE` — 0166bd1228bf4c467277411efd4ecfd49f824d65
- `STEVE_HEAT_MEASURE_BEFORE_THE_SCREWDRIVER` — 84f6ba081660f1880c5213e2b9bd0416eb7a983f
- `DESIGNER_BRIEF_TUNE_MINED_FROM_TODAYS_BRIDGE` — af1b5fbde5
- `DESIGNER_BRIEF_TUNE_MINED_FROM_TODAYS_BRIDGE` — af1b5fbde5
- `CONDUCTOR_PROMPT_WIRE_SEND_IT_AGAIN_LINE` — 01928980e326b547afc90d46c939ce684849ee57
- `CONDUCTOR_GOODBYE_FIX_QUEUED_WAIT_SKIPPED` — 7d29922ff0f5a17a2aa13dcaabdf7d08f6365911
- `DISPATCHER_PROVE_BLOCKED_TOP_AND_CURSOR` — 1205f24aa92748989f3c92ea0155456e613699f7
- `PUBLISH_ALARM_HARDEN_FRESH_LOCK_IS_TRAFFIC` — 05adfa64255c43b59cf3bb9eb48f40c320a65eb5
- `CALL_DEADLINES_ENFORCE_130_OPEN_ENDED` — 7a9249afe882412e83693f01d7b20e68c4a658d6
- `STEVE_STEWARD_FIX_PLANNED_OUTAGE_CRIED_WOLF` — 7abee9a0c2b56da32f0a3686d3603cb5953e4b80
- `PULSE_DEPLOY_UNSTICK_DIRTY_CHECKOUT` — 2fc8d23cf995db2a8ec07493d9282d906cc85e46
- `TIMER_ALARM_SILENCE_TEST_LITTER_COUNTED` — 11aa6205a789b5fd812801f3991b9b4af1faec04
- `RELENTLESS_GAME_PROVE_REIMPLEMENT_AFTER_FAIL` — e348a3347f182597e42432314b9a34e1d42e3744
- `PULSE_DEPLOY_GUARD_SOMEONE_WALKED_IN` — de44537a987d22cd8aa917b924f6229838350ec9
- `SCRATCH_STRANDED_FIX_SHARDS_CRY_WOLF` — 1aaa1987cd90729447fe041199368b9a6f947aa6
- `OPS_RELENTLESS_BOOKS_UNSTICK_WGYL` — 5caff7b55db93368b5f3c7772c8665d330a91da1
- `RELENTLESS_CRITERIA_SYNC_AFTER_RETIER` — 85a9d6172cc4f7f5b6dc8bc906745d29f0ab5a72
- `OPS_FINDINGS_DIAGNOSE_XZLM` — f285a46b6bf51e980b4dbefb27f31e47e78ea602
- `RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK` — 932875eaea81fc6a9c8eaec4de35d49ffcd24965
- `RELENTLESS_TICK_PROVE_FIRST_SHUFFLE_BIT` — 528b6d6ab49642cbeb7c98a7360586b6dfb9ffa9
- `RELENTLESS_WATCH_SELFTEST_FIX_FIXTURE_GAPS` — 4372e92aa3210f85dbcbec8a61c16bf7a43758dc
- `RELENTLESS_FILLER_FIX_TOO_KEEN_ON_PARKED` — 9aab2421bef6527ee37994b06ee4474578ad72df
- `RELENTLESS_SELFTESTS_FIX_STANDING_REDS` — 612416958f3f87ac63be40183b30e63b82e90d19
- `OPS_MEMORY_VET_THEN_WIRE_AFTER_WATCH` — ac39eccf390ee7ba06fec42a29b4cdf135f15381
- `SELFTEST_CONDUCTOR_AUTH_FIX_PREEXISTING_RED` — dccec846c1952d1cf1a7915582155217becfff40
- `DESIGNER_LESSONS_ABSORB_JOINT_SESSION_DAY` — e42ec37412
- `DESIGNER_LESSONS_ABSORB_JOINT_SESSION_DAY` — e42ec37412
- `TESTQ_ARCHMAGI_LANE_BUILD_BACKFILL` — 4d19db627979ac5313f1452aaeed9891ff0c0e83
- `RELENTLESS_REVIEW_FINISH_POOL_LEVELLING` — e8411a141d3cd2344d1aae9d4d36b86ce5faf352
- `FOUNDRY_SEAT_RETIRE_ALARM_STILL_MOURNING` — 5f0230ddec2fe07565f811f92ecfd8df4a787405
- `TESTQ_MODS_WIRE_BEYOND_FLOWWORKS` — 7379a46fcf16753a4ddae199385175c71e66632b
- `FOUNDRY_CLONE_UNITS_MIGRATE_TO_BENCH` — 95c46f4c775cd45afcb8bd993b38dc5dd5e305ff
- `TESTQ_FILLER_DIAGNOSE_FAILS_NOBODY_HEARD` — 286bed378d76eec60dabbe791c3890e9ea27976a
- `SELFTEST_FIX_SIX_TIMEOUTS_AT_240S` — 40134890c7980ec9479b20480396eb9a373fc0be
- `PIPELINE_BUDGET_ENFORCE_HEAL_THYSELF` — be632d1848ba722cec118c48435d0c2cc872cccd
- `HARNESS_BOTTLENECK_MEASURE_WHO_WAITS_ON_WHOM` — 6def8c6f7c71a7792ac9780fc45f8e6b25c3e3d2
- `BRIDGE_DEADLINES_UNIFY_ONE_ABSOLUTE_POLICY` — 80b0be06bb09b71c5fa722732be8cab82c569279
- `MODCHECK_SWAP_FIX_OUTSIDE_TRY` — 9f01f4bdcea3ac8cf446de9cbbf1234e2458da41
- `AGENT_WRAPUP_ENFORCE_ASKING_NEVER_WORKED` — 3e0b001eb480055a614dd16fa479a2c0362df79f
- `LOAD_WAIT_FIX_BLIND_PROBE_WAITS_FOREVER` — aa0f59755d3eaebd6d38f78987fcaa3039c43965
- `MODCHECK_SESSION_FIX_STALE_LIST_ACCEPTED` — 3021d26a0252a309fcf0cf273a19fd7ce35246af
- `SHARD_LEVEL_FIX_APPEND_LOST_MIDRESTORE` — c512f6bd9a6ff0bc4669bc3c678cfaf6f38d14a5
- `TOOLS_PURGE_VALIDATOR_VET_UNREVIEWED` — 17658d6fa93531da0f5a01b3d09c394a0f7351df
- `FIRST_TOUCH_BUILD_DESIGNER_READS_FIRST` — d583a3d7858b0cf2b8dca51415be2be6e7a470c5
- `LIVE_ROWS_FIX_STOP_GUESSING_LOGS` — 582e7241b2391ae8517124d223aaa63a6a6f7456
- `BRIDGE_HOOKS_HARDEN_REENTRANT_AND_FAULTY` — ac4ac790dabcb5de07a03038b09dddc632029d5f
- `NIGHTLY_COP_FIX_RED_CYJJIB_ARBP` — aae3f1ee6fab260751a11f6bf8b36742c0ff86f3
- `VALIDATOR_REPLAY_BUILD_GOOD_AND_BAD` — 750a006a8386c94ed31a96855cb430e172adab66
- `DESIGNER_STAGES_REBUILD_LAUNCHER_HOLDS_LEASH` — c2c19833ccfa351d5519734e466e2a20be8b1df2
- `RED_COP_BUILD_NO_ORPHAN_REDS` — f0492bc10c570405313f9ae24d5df7b159904e82
- `OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS` — d281d6261d5f
- `OPS_CHURN_MEASURE_RETURNS_ARE_NOT_PROGRESS` — d281d6261d5f
- `BOOKS_STALE_FIX_OPS_CANNOT_SEE_IT` — cefb739a823e7d16711995aca3105ffa0665f2cf
- `CHURN_BREAKER_BUILD_RETRY_NEEDS_A_WARRANT` — 5b7b901893b9299e8832564c50a7902e7e2d3fb8
- `OPS_LIVES_CENSUS_EVERY_DEATH_READ_ONLY` — bb45c9df1318c58bc350946a26233c91dfbc3959
- `POOL_FIX_STATE_COMMITS_PIN_CLONES` — 62223b308b7c8d27838d4a4a3ba18519f2b6bac2
- `RELENTLESS_LINE_FIX_ONE_MOD_CLOGS_ALL` — 24a7e0f17ef30f03eebf5e75b6c03f0a54ff1f88
- `TESTQ_FIX_ROW_ITEMS_FIRST_ALPHABETICAL` — 1497e523becc3ba240c626013cad895bdc3bc7d9
- `TESTQ_WORKER_MIGRATE_PYDANTIC_CONTRACT` — f96e761d5c3308f77d7b2caa05e3bd45e49c61a2

## Filed and still open (129) — the next seat's queue

- `DRAWBRIDGE_SWING_DESIGN_LESS_RIDICULOUS` — Design how a drawbridge leaf and gate move when opening and shutting, in all four directions, so it does not look ridiculous; offline motion study fir
- `STEVE_FILLER_DIAGNOSE_NINETY_CHAINS_HELD` — SteveDesktop's filler is EXHAUSTED: FlowWorks has 90 chains held for a repair and 18 DRY, so the unbraked lane stays idle
- `STEVE_FILLER_DIAGNOSE_NINETY_CHAINS_HELD` — SteveDesktop's filler is EXHAUSTED: FlowWorks has 90 chains held for a repair and 18 DRY, so the unbraked lane stays idle
- `OWNER_HOLD_TEST_REPAIR_FALLBACK_WENT_QUIET` — selftest_owner_hold row 'the act fell back to the ledger: the take refuses' is red on clean HEAD 722482bfc1 too: with an unwritable act stamp, the tak
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — Stopping a detached unit leaves its claude alive: the wrapper bash dies, claude lives on in its own claude-seat-BENCH-<unit>.scope. Seen 2026-11-03: u
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — Stopping a detached unit leaves its claude alive: the wrapper bash dies, claude lives on in its own claude-seat-BENCH-<unit>.scope. Seen 2026-11-03: u
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — Stopping a detached unit leaves its claude alive: the wrapper bash dies, claude lives on in its own claude-seat-BENCH-<unit>.scope. Seen 2026-11-03: u
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — Stopping a detached unit leaves its claude alive: the wrapper bash dies, claude lives on in its own claude-seat-BENCH-<unit>.scope. Seen 2026-11-03: u
- `DETACHED_STOP_FIX_ORPHAN_KEEPS_BILLING` — Stopping a detached unit leaves its claude alive: the wrapper bash dies, claude lives on in its own claude-seat-BENCH-<unit>.scope. Seen 2026-11-03: u
- `RESTART_DOCS_FIX_CONDUCTOR_SAYS_NOW_TWICE` — selftest_restart_now RED: conductor.md names --now twice since b483dac198 (line 91 and 96); the test wants exactly once
- `RESTART_DOCS_FIX_CONDUCTOR_SAYS_NOW_TWICE` — selftest_restart_now RED: conductor.md names --now twice since b483dac198 (line 91 and 96); the test wants exactly once
- `SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP` — BENCH survives as a seat key shared by the Conductor window and Relentless workers, a clone path, role files, units and prose. Census and three-step a
- `INTEROP_RETRY_FIX_EIGHTY_SCRIPTS_LEFT` — 79 selftest lines still launch their built exe by bare subprocess.run, so a WSL UtilAcceptVsock launch timeout reads as a red test: move them to winbu
- `CONDUCTOR_RESET_FIX_KILLED_MID_READ` — The Conductor window's context-limit restart fires 20 s after a turn ends, so it wiped the reply he was reading; wake should re-show the old window's 
- `WINSTAGE_CULL_THREE_GIGS_PER_KERNEL` — selftest_winstage.windows_project_path still rsyncs the whole 3 GB src with --checksum for 12 callers (flowworks_kernel_oracle, flowworks_sheet, floww
- `RESTORECHECK_WIDEN_POSITIONAL_SLIPS_NET` — proof_restore_check: a setter wrapper called in a finally with a positional literal is not seen as restores-fixed-value
- `PROOF_CRASH_FIX_READ_AS_MOD_FAILURE` — A proof script that crashes exits 1, and relentless_live writes that as a FAIL verdict on the mod: 15 of 47 FAIL rows with logs in live/runs.jsonl (to
- `PIPELINE_RENAME_WORKERS_NOW_SWAPPABLE` — Name it the Relentless Pipeline, with Relentless-style Builder/Judge workers from MandrakeWorkflows in its places; rename in pages and docs, and split
- `RESTOREWAIVER_AUDIT_TEN_TAKEN_ON_TRUST` — restore-check: ok silences a hit whether or not the restore exists. selftest_proof_restore_check.py now audits the 5 files NIGHTLY_COP_FIX_RED_CYJJIB_
- `BRINGBACK_SELFTEST_FIX_ALREADY_SEVENTEEN_RED` — selftest_idle_bringback.py fails 17 checks and takes 5 min on a clean HEAD export (24d9a9d483): no kill at the limit; found while landing CONDUCTOR_RE
- `BRINGBACK_SELFTEST_FIX_ALREADY_SEVENTEEN_RED` — selftest_idle_bringback.py fails 17 checks and takes 5 min on a clean HEAD export (24d9a9d483): no kill at the limit; found while landing CONDUCTOR_RE
- `RESTART_NOW_TEST_FIX_COUNTS_TWO` — selftest_restart_now.py requires roles/conductor.md to name --now exactly once; HEAD 24d9a9d483 names it twice (line 93 and the CONDUCTOR_REBOOT_FIX_T
- `RESTART_NOW_TEST_FIX_COUNTS_TWO` — selftest_restart_now.py requires roles/conductor.md to name --now exactly once; HEAD 24d9a9d483 names it twice (line 93 and the CONDUCTOR_REBOOT_FIX_T
- `FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING` — Remove Fleet Watch's leftovers once RUNNING_NOW carries its parts: rm-fleetwatch.service and .timer in src/RimMandrake/Utils/systemd, fleet_refresh.py
- `SELFTEST_RETRY_FIX_25_STILL_BARE` — 25 python files launch 'dotnet run' without winbuild.run_interop, so a WSL accept4 launch timeout under load reads as a failed test
- `SELFTEST_RETRY_FIX_25_STILL_BARE` — 25 python files launch 'dotnet run' without winbuild.run_interop, so a WSL accept4 launch timeout under load reads as a failed test
- `TIMERS_PRUNE_AUDIT_FINALLY_READ` — Operations timers: enact the audit's slow, merge and retire verdicts one by one, each proved still running or cleanly gone, dropping the retired names
- `BIOMES_PORT_PRUNE_FORTY_TWO_HITCHHIKERS` — Drop survey buckets A and B of the Biomes! port as one closure (42 creatures with their eggs, bodies and sounds) and drop RSW_Thrumbungus with RSW_Thr
- `STAGE_WAKE_TUNE_NAPS_AFTER_LOAD` — A staging worker's relentless_game.ready does not wake game_pass, so the first proof after a load still waits for the next tick. A wake inside lease a
- `NEEDS_YOU_DRAIN_NINE_ALREADY_ANSWERED` — Nine open items routed to the owner already hold his later note, so the page lists them as answered: route each (rebuild, close or give back with need
- `MODS_ACCEPTED_DECIDE_ZERO_OF_THE_LOT` — The page's 'mods accepted' is modcheck GREEN at today's code: 0 of 133 (6 green at older code, 60 red, 4 draft, 63 never run). No other record of acce
- `PLAYER_EXPECTATIONS_DOCUMENT_NONE_WRITTEN` — Live Testing has a 'falsified player expectations' tile the owner asked for, reading 'not recorded': nothing writes such a record. Give live proofs a 
- `RELENTLESS_FIX_PARKED_RUN_WORKS_ON_ANYWAY` — relentless: a run already working when the owner blocks its item keeps going, and may land and be checked; lease() now stops only the next worker
- `RELENTLESS_FIX_PARKED_RUN_WORKS_ON_ANYWAY` — relentless: a run already working when the owner blocks its item keeps going, and may land and be checked; lease() now stops only the next worker
- `RUNNING_PAGE_BUILD_TOKEN_FUEL_GAUGE` — RUNNING_NOW: show each of the three accounts' week % remaining and time to reset (account_usage.py), and for each a clear ahead/equal/behind reading o
- `BREAKER_SELFTEST_FIX_ONE_RED_IN_THIRTEEN` — selftest_relentless t_breaker_di2 went red once in about 13 runs: 'the roads that landed are not repeated while told retries' and 'told lands once it 
- `GUARD_SEAM_DECIDE_KEPT_WALKS_OUT_UNGUARDED` — A sweep's 'live --result kept' returns a fix that died to done with no close, so the close gate of REPEAT_ALARM_ENFORCE_GUARD_OR_STAY_OPEN never sees 
- `MARKER_WALL_FIX_HOST_LOG_BEHIND_GLASS` — The Marker's wall (relentless_rules.json walls.marker.tmpfs) puts an empty tmpfs over /mnt/d/ClaudeWork/rimmandrake, so a clause about host state ther
- `ALARM_ROUTE_FIX_RESTORE_INCOMPLETE_ORPHAN` — selftest_incident FAILs 'every alarm kind is in the routing table': restore_incomplete (relentless.py:1563, added by 7684d1bcbe) has no row in alarm_r
- `ALARM_ROUTE_FIX_RESTORE_INCOMPLETE_ORPHAN` — selftest_incident FAILs 'every alarm kind is in the routing table': restore_incomplete (relentless.py:1563, added by 7684d1bcbe) has no row in alarm_r
- `ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE` — role_launch.unit_state: systemctl show returning nonzero for a collected or never-created unit/scope reads 'unknown', and supervision treats unknown a
- `ROLE_UNITSTATE_FIX_GHOST_RUNS_NEVER_LEAVE` — role_launch.unit_state: systemctl show returning nonzero for a collected or never-created unit/scope reads 'unknown', and supervision treats unknown a
- `ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES` — role_launch.py review g2r2 leftovers (pre-existing): (1) decide_roles' degraded ops reading fabricates week_left 100.0, so a stricter week_left_pct_lt
- `ROLE_LAUNCH_HARDEN_FLOOR_AND_ODD_NAMES` — role_launch.py review g2r2 leftovers (pre-existing): (1) decide_roles' degraded ops reading fabricates week_left 100.0, so a stricter week_left_pct_lt
- `NOW_FLAG_FIX_NAMED_TWICE_OOPS` — selftest_restart_now is RED on main: src/RimMandrake/rimflow/roles/conductor.md names --now twice, the test wants exactly once (last conductor.md comm
- `GSS_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS` — Designer deep pass on GimmeSomeSlack (GSS): read its proof scripts, name each scene's missing site prep and control case, and file the build items for
- `SOLAR_SCRIPT_MEASURE_SITE_PREP_AND_CONTROLS` — Designer deep pass on Solar: read its proof scripts, name each scene's missing site prep and control case, and file the build items for Relentless
- `BAROQUE_SCRIPT_MEASURE_PREP_AND_CONTROLS` — Designer deep pass on Baroque Biomes: read its proof scripts, name each scene's missing site prep and control case, and file the build items for Relen
- `FLOWWORKS_SCRIPT_MEASURE_PREP_AND_CONTROLS` — Designer deep pass on FlowWorks: read its proof scripts, name each scene's missing site prep and control case, and file the build items for Relentless
- `RELENTLESS_REOPEN_FIX_DONE_MEANS_FOREVER` — relentless.py enrol skips every item already in the store, done ones included (ours = all states), and reenrol takes only retired: a ledger item Relen
- `RELENTLESS_REOPEN_FIX_DONE_MEANS_FOREVER` — relentless.py enrol skips every item already in the store, done ones included (ours = all states), and reenrol takes only retired: a ledger item Relen
- `LIVE_ROLE_FIX_END_OF_DAY_ALIBI` — live_line._role_last dates a role launch at the END of its recorded day: a launch before the commit passes not_before the same day, and freshness runs
- `STEVE_SPAWN_FIX_COPIES_THE_PAST` — worker.py spawn copies worker.py/schema.py/companion_identity.py into outer/ AFTER cmd_start pins the clone (checkout --detach source_sha) with CLONE=
- `TESTQ_ITEMOWED_FIX_DEFS_CHAIN_ADOPTS_ALL` — gaps.py item_owed links a generic chain name (defs, defs_resolve) to an unrelated item: fill_rank for Stillsand, Contagion, TerminalBiomes and Environ
- `TESTQ_ITEMOWED_FIX_DEFS_CHAIN_ADOPTS_ALL` — gaps.py item_owed links a generic chain name (defs, defs_resolve) to an unrelated item: fill_rank for Stillsand, Contagion, TerminalBiomes and Environ
- `FLOWWORKS_TOGGLES_BUILD_SIX_PREDICATES_OWED` — FlowWorks: six toggle chains have never measured a row since they were written: fall_damage, liquid_corrosion, liquid_drilling, liquid_ignition, super
- `RIVER_STEAM_WIRE_PYRELANDS_STEAMLESS_ON_TEST` — toggle_river_steam_pyrelands never measures: the map is re-tiled to RM_Pyrelands correctly but RiverSteamBiomeExtension is added only by mandrake.rut.
- `PROOF_HOSE_FIX_GATE_RED_ON_STEVE` — hose_live_rows (30 rows) has never measured: on SteveDesktop the proof_hose_live driver spends ~1010 s in its offline gate, csharp_selftest (Utils/sel
- `CHECKER_SANDBOX_FIX_BLIND_TO_STEVE` — Relentless's blind checker runs in a sandbox that cannot ssh SteveDesktop and sees an empty D:\ClaudeWork, so an item whose proof lives on another mac
- `CHECKER_SANDBOX_FIX_BLIND_TO_STEVE` — Relentless's blind checker runs in a sandbox that cannot ssh SteveDesktop and sees an empty D:\ClaudeWork, so an item whose proof lives on another mac
- `STEVE_FILLER_MONITOR_FAIL_FINDINGS` — Standing host for the testq filler's FAIL rows: ingest records each item-less job with a FAIL row as a failed run here plus one UNTRIAGED finding per 
- `STEVE_FILLER_MONITOR_FAIL_FINDINGS` — Standing host for the testq filler's FAIL rows: ingest records each item-less job with a FAIL row as a failed run here plus one UNTRIAGED finding per 
- `STEVE_FILLER_MONITOR_FAIL_FINDINGS` — Standing host for the testq filler's FAIL rows: ingest records each item-less job with a FAIL row as a failed run here plus one UNTRIAGED finding per 
- `MARKER_DIFF_FIX_EARLIER_WORK_LOOKS_EMPTY` — The Marker's box change.diff covers only sha^..sha, so work an item landed in an earlier commit (the candidate sha is a later report or proof commit) 
- `INHABITED_DESIGN_FIRST_TOUCH` — Designer deep pass on Inhabited (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), c
- `SWBESTIARY_DESIGN_FIRST_TOUCH` — Designer deep pass on SWBestiary (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), 
- `UTINNIPATCHES_DESIGN_FIRST_TOUCH` — Designer deep pass on UtinniPatches (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene
- `ATLAS_DESIGN_FIRST_TOUCH` — Designer deep pass on Atlas (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), certi
- `ORACLE_DESIGN_FIRST_TOUCH` — Designer deep pass on Oracle (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), cert
- `ATMOSPHERICBASE_DESIGN_FIRST_TOUCH` — Designer deep pass on AtmosphericBase (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `MINERALS_DESIGN_FIRST_TOUCH` — Designer deep pass on Minerals (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), ce
- `PYRINTH_DESIGN_FIRST_TOUCH` — Designer deep pass on Pyrinth (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), cer
- `TILEFEATURES_DESIGN_FIRST_TOUCH` — Designer deep pass on TileFeatures (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene)
- `ARMOURY_DESIGN_FIRST_TOUCH` — Designer deep pass on Armoury (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), cer
- `SHIPVERMIN_DESIGN_FIRST_TOUCH` — Designer deep pass on ShipVermin (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), 
- `COLDSTORAGE_DESIGN_FIRST_TOUCH` — Designer deep pass on ColdStorage (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene),
- `ASSAILANTSALVAGE_DESIGN_FIRST_TOUCH` — Designer deep pass on AssailantSalvage (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sc
- `LUMINOUSPIGMENT_DESIGN_FIRST_TOUCH` — Designer deep pass on LuminousPigment (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `BACTA_DESIGN_FIRST_TOUCH` — Designer deep pass on Bacta (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), certi
- `BRAINWORMS_DESIGN_FIRST_TOUCH` — Designer deep pass on BrainWorms (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), 
- `GIZKASTOWAWAY_DESIGN_FIRST_TOUCH` — Designer deep pass on GizkaStowaway (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene
- `GRAFFITIIMPERIAL_DESIGN_FIRST_TOUCH` — Designer deep pass on GraffitiImperial (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sc
- `DROIDREPAIRJOBS_DESIGN_FIRST_TOUCH` — Designer deep pass on DroidRepairJobs (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `EGGRECKONING_DESIGN_FIRST_TOUCH` — Designer deep pass on EggReckoning (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene)
- `PYRELANDSMECHANICS_DESIGN_FIRST_TOUCH` — Designer deep pass on PyrelandsMechanics (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per 
- `RITES_DESIGN_FIRST_TOUCH` — Designer deep pass on Rites (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), certi
- `ACOUSTICSCANNER_DESIGN_FIRST_TOUCH` — Designer deep pass on AcousticScanner (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `TROPHYCRAFT_DESIGN_FIRST_TOUCH` — Designer deep pass on TrophyCraft (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene),
- `CUISINE_DESIGN_FIRST_TOUCH` — Designer deep pass on Cuisine (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), cer
- `GRAFFITI_DESIGN_FIRST_TOUCH` — Designer deep pass on Graffiti (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), ce
- `EMPIREPURSUIT_DESIGN_FIRST_TOUCH` — Designer deep pass on EmpirePursuit (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene
- `WASTERUN_DESIGN_FIRST_TOUCH` — Designer deep pass on WasteRun (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), ce
- `SARLACC_DESIGN_FIRST_TOUCH` — Designer deep pass on Sarlacc (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), cer
- `WRECKEDMACHINES_DESIGN_FIRST_TOUCH` — Designer deep pass on WreckedMachines (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `STARWARSRACES_DESIGN_FIRST_TOUCH` — Designer deep pass on StarWarsRaces (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene
- `STARWARSPATCHES_DESIGN_FIRST_TOUCH` — Designer deep pass on StarWarsPatches (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `MANDRAKEPATCHES_DESIGN_FIRST_TOUCH` — Designer deep pass on MandrakePatches (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `WATCHERS_DESIGN_FIRST_TOUCH` — Designer deep pass on Watchers (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), ce
- `AFTERMATH_DESIGN_FIRST_TOUCH` — Designer deep pass on Aftermath (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), c
- `GRAVSHIPLANDING_DESIGN_FIRST_TOUCH` — Designer deep pass on GravshipLanding (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per sce
- `STRUCTUREINJECTIONSSW_DESIGN_FIRST_TOUCH` — Designer deep pass on StructureInjectionsSW (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls p
- `RIMPROPERTY_DESIGN_FIRST_TOUCH` — Designer deep pass on RimProperty (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene),
- `HUGETHINGS_DESIGN_FIRST_TOUCH` — Designer deep pass on HugeThings (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene), 
- `LIVEROUND_SHRINK_PROOFS_ARE_THE_SHORT_PART` — Live rounds on 2026-11-03 held the game 11.0-11.5 h but proof commands ran 1.58 h of it, and 139 of 265 clause runs came back UNMEASURED (38 REFUSED):
- `CLONEPOOL_FIX_GAME_WAITERS_HOG_THE_POOL` — On 2026-11-03 staffing was refused 'pool full' for 4.9 h (21% of the day) because items waiting for the game phase keep their work clones (16/16, 64 o
- `TESTQ_SURPRISE_DIAGNOSE_SCRATCH_HALTS_CHAINS` — testq: five FlowWorks chains (bottle_revert, dig_finds, liquid_heat, plot_C2_tar_and_fluids, swept) end HARNESS-held every newest run because safe_adv
- `FUEL_MOAT_WIRE_EMPIRE_PURSUIT_NOT_INVITED` — testq FlowWorks/fuel_moat_astrofuel utinni_blast_summons_raid + astrofuel_detonation_off_burns UNMEASURED every run: RimUtinni Empire Pursuit is not o
- `FILL_TIER_BUILD_HALF_NOTCH_SETTER_MISSING` — testq FlowWorks/plot_B_fill_tiers UNMEASURED (not on this map): no bridge tool sets a fill under one notch (excavation_drive setFill is whole notches)
- `WORKS_RUINS_BUILD_PREDICATE_TWO_FRESH_MAPS` — testq FlowWorks/machinery_found_works: 3 rows 'owed, no predicate yet' (liquidWorksRuinsEnabled and liquidWorksRuinStockEnabled are map-generation tog
- `FIRE_RAIN_DIAGNOSE_BRIDGE_NAPS_MID_DOUSE` — testq FlowWorks/fire_rain: rain_douses_open_fire FAILs with RimBridgeError timed out after 30 s (long event / frame-bound call), so rain_off_leaves_fi
- `BREAKER_ROADS_TEST_FIX_FLAKY_UNDER_LOAD` — selftest_relentless.py t_breaker_di2 'roads that landed are not repeated while told retries' + 'told lands once it can' FAILED once in a 27-test paral
- `MODCHECK_SELFTEST_FIX_ZOOM_GUARD_GATECRASHES` — modcheck/selftest.py t_compose_test_list_appends_once_and_reads_back FAILS on main: compose_test_list now prepends zoom_guard.ZOOM (ray1203.simplecame
- `ARTLEDGER_SELFTEST_FIX_FIXTURE_NEVER_WRITES` — src/RimMandrake/Utils/art/selftest_art_ledger_fixes.py crashes before a verdict on HEAD 89ca56e5ee: git_fixture() runs git add infrastructure/state/ar
- `ART_PURGE_FIX_BYTES_GONE_BEFORE_RECEIPT` — artledger.purge unlinks the store bytes before w.flush() writes the purge event; a crash between them loses the picture with no purge record. Write th
- `BRIDGE_PENDINGCALL_RECONCILE_INDETERMINATE` — A live proof that hits rimbridge_client IndeterminateError (a mutating call with a lost reply) dies; nothing runs the read-only reconcile, so the next
- `SUMP_PROOF_HARDEN_IMPLAUSIBLE_READ` — SUMP_GLASSWALK_SPEED_RATIO_1 proof scored a FAIL from an implausible reading (12 cells walked in 2 ticks): a speed ratio needs a plausibility floor th
- `SCARLANDS_PACKAGEID_CORRECT_ABOUT_MISMATCH` — Deployed Scarlands About.xml has no readable packageId, so the modlist gate refuses ART_OVERRIDE_FAMILY_SCRIPT_1 on every staging (game.harness=4). Re
- `VITALS_PROOF_ENFORCE_TIER_DECLARED` — VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL proof printed WRONG_TIER/WRONG_LIST then exited 1 on A1 and A2: the item must declare the full-list tier it nee
- `HORRORS_WORLDCSV_SYNC_STALE_PROOF` — HORRORS_RAIDING_FACTION_1 A2 read 0 nightside tiles from a stale world CSV and scored FAIL: the proof must refresh or date-check the CSV and read UNME
- `HEALTHCHECK_COMPANION_VERIFY_STALE_DLL` — HEALTH_CHECK_MONITOR_MEMORY_TPS_OVER_TIME proof read None for every metric (a companion tool missing from the deployed JawaBench DLL) and scored FAIL:
- `CONTRACT_BINDING_UNTANGLE_WHAT_FROM_HOW` — Split each contract into a versioned obligation (what must be true) and binding (scenario, proof, execution location, fixtures, freshness); an indepen
- `CLOSE_AUDIT_MEASURE_FALSE_CLOSES_HONESTLY` — Metrics: accepted delivery yield by intake cohort, end-to-end cost, rebuild waste before attribution, instrument availability, repeat waste, attributi
- `MODCHECK_COMPOSE_FIX_STALE_CAMERA_SURPRISE` — src/RimMandrake/Utils/modcheck/selftest.py is RED on main: 'compose: only the missing id is appended' gets ['ray1203.simplecamerasetting', 'mandrake.r
- `MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD` — verify_loaded_list reports a composed mod that is not installed on the host as a stale load, so the worker spends a restart that cannot help; name it 
- `ANTIQUITIES_DESIGN_FIRST_TOUCH` — Designer deep pass on Antiquities (first touch): read its code and spec, expand the spec and validation strategies (site prep and controls per scene),
- `LIVEROUND_COMPANION_DEPLOY_OLD_DLL_BLAMED` — The relentless live round deploys mod folders only (live-deploy) and never the JawaBench companion (BridgeTools/JawaBench, src/RimMandrake/bridgetools
- `STAGING_COMPANION_BUILD_STILL_YESTERDAYS` — Relentless live staging deploys mod trees but never rebuilds/deploys the JawaBench companion DLL (BridgeTools/JawaBench/JawaBench.BridgeTools.dll), so
- `INCIDENT_STORES_UNIFY_TWO_BOOKS_ONE_FAULT` — Relentless now keeps two incident stores that share no records: relentless_breakers incidents.json and the new instrument_incidents.json (52277abce1).
- `REPAIR_FIXTURES_ENFORCE_VERDICT_AT_FILING` — An instrument incident releases only when its repair's good/bad check commands print FIXTURE_VERDICT: PASS|FAIL (52277abce1). A repair item filed with

## Commits

```
5a14b6110f conversations: catch-up 22 record(s)
d7bcc58fb5 ledger: file two follow-ons of the attribution gate
537e76ddd7 ledger: DISPATCHER notes (1)
97cf4cc2c9 ledger: close REWORK_GATE + INSTRUMENT_INCIDENT at 52277abce1; review receipts; lesson
6ca95fc03e SCRATCH_CLONES_SHRINK_SPARSE_NOT_FULL: scratch clones default to a sparse tooling cone, not the whole tree
4693c82edc HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS: review record for the registration selftest
bae1f3c8ed HOOKS_VERIFY_TRUE_SUFFIX_MAY_MUTE_REFUSALS: selftest runs every registered hook command for allow, deny, crash
b856624fa8 BRIDGE_LOAD_FIX_READY_WHILE_INITIALIZING: hold load_game_ready success until programState Playing
694d29e841 ledger: DISPATCHER notes (1)
a93f4dc0b7 OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE: review record for the guard test
68f98f903d OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE: guard test on the real schedule
1d4ba9e143 ledger: relentless supervisor
6ece0a9fbf ledger: DISPATCHER notes (1)
07862bbc41 ledger: RUNNER ingest of 1 testq job(s)
52277abce1 INSTRUMENT_INCIDENT / REWORK_GATE: GPT review 2 fixes (fixture verdict line, close receipt fenced after the run, done_index receipt)
8cdd7cdbff ledger: DISPATCHER notes (1)
42d9f1684c ledger: RUNNER ingest of 0 testq job(s)
e92cc041c4 ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG: review mark for the proof
c56b2e6fd5 ARTPIPE_DONE_RECORDS_AUDIT_LOST_PNG: re-derive installed decisions at HEAD; git-free proof
3adc9ba489 ledger: relentless supervisor
... 666 more: git log --oneline 6f251e736a..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     relentless staging WARSCAR_HOSPICE_DESERTERS_1: deploy and restart for its live proofs

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/art/events/BENCH.jsonl   art pipeline daemon (BENCH shard, not this window)
 M infrastructure/state/code_review/BENCH.jsonl   helpers' review marks, appended after their publish
 M infrastructure/state/ledger/events/RUNNER.jsonl   RUNNER seat (not this window)
 M src/RimMandrake/FlowWorks/northstar/review/scenarios/map_r_placed.json   a FlowWorks review-sheet server (dirty since before this window)
?? cards.json   untracked, predates this window
?? design/RimMandrake/designer_drawing_out.md   another session's Designer draft, untracked
?? shortcuts.ps1.txt   untracked, predates this window
```

