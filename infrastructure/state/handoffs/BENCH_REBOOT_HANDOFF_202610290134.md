# BENCH_REBOOT_HANDOFF_202610290134 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610281706`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**This window is now the Conductor (v3 design §2: no BENCH seat; the Conductor absorbs Bench, its helpers are session-only).** Tonight's trial is mid-runbook: `design/RimMandrake/rimflow_v3_trial_night_2026-10-28.md`. Done before the switch (all published): cutover applied d302fbbcea (691 items BENCH→FOUNDRY, 40 kept), FOUNDRY helper budget 6 on his word, Arbiter/Producer/Auditor/Innovator enabled 60f6a6c96c (dispatch clone pulled), seat_restart enabled DRY 38c4fe7052. Owner's go, verbatim: *"I am back at the hotel. Let's get to it!"* The account switch to steven (`claude-account use steven --confirm archmagi`, via a detached systemd unit) is the last act of this window and kills it.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Account switching is paused on his order ("disable any script that will auto log me out for awhile and stay on this account"); tonight's steven switch is his explicit request. account-plan.timer and claude-account-warm.timer are OFF; HOLD file present. Auto-warm of idle logins DID go live via the self-updating pulse-deploy checkout (re-checks the live login under the switcher's lock).
- Three FlowWorks spike items are parked for a live session WITH him (HOSE_WATCH_ALLOC_HUNT_GC_IN_TICK, WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE, WALLREACH_RELABEL_TAME_SLICED_BUFFERED): his words "Let's not keep chasing the slowness spike"; the question is whether max-step/GC bars can be waived as game stutter.
- Mineral sheet for his review: https://claude.ai/artifact/H82d4dLjyqGtudGG33D48i (edits in its db collection 'edits'); nothing ships until he reviews (D10).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
- `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` -- trial running; NEXT: after relaunch, verify FOUNDRY and the Conductor woke (journal ring + armed/FOUNDRY.json new session), run `python3 src/RimMandrake/rimflow/role_launch.py run-now --role Innovator --by BENCH --why "v3 trial night: first run" --apply` once the account band is not RED, run `python3 src/RimMandrake/rimflow/v3_ready.py`, then do runbook §6 first-hour watch and write night.md.
- `RIMFLOW_V3_BUILD_DISPATCHER_FIRST` -- live; NEXT: check the 19:30 Operations / 20:00 Conductor runs came in under the new weighted caps (journal 'weighted tokens'), and the first seat_restart dry ticket ('would SIGTERM') before `install_wt_seat_profiles.py --only FOUNDRY --apply` and dry:false.
- `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY` -- applied d302fbbcea; NEXT: close it once FOUNDRY has claimed one moved FlowWorks item; revert with `v3_cutover.py revert --owner-said "…" --commit` if needed.
- `MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER` -- sheet published; NEXT: read his edits (ArtifactData list collection 'edits') when he says he's tuned it.
- `HELPER_BUDGET_MIGRATE_INTO_DISPATCHER` -- closed bce8d5a772; Conductor helpers 0 (sitting cap 6% reached), FOUNDRY 6 by his word; NEXT: confirm helper_budget.json shows FOUNDRY 6 after the relaunch.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- queue_lint ledger guard false-positive on a word-boundary "rm" before a ledger path (fixed 920a18cb76) (filed: lessons).
- A low mutation score can be a TARGETS wiring bug (filed: lessons).
- Codex ran 46% of its week in a day on review rounds; reviews stay on Codex by his word, one round per change (see: memory gpt-does-reviews).

## Closed since the last handoff (16)

- `ARTEVAL_COMPARE_VETO_FIX_ACCEPT_LIMBO` — a6b839b8a2d1
- `THIRST_STORE_TANK_DIAGNOSE_LATE_BRINE` — ad2f5912e4
- `FURNACEBEAST_ART_INSTALL_OWNER_KEPT_IT` — 7d9cf3d836
- `SURFACEGAP_PARITY_FIX_TIES_ARE_UNSORTED` — a77dbfed0b
- `HOSE_TICK_REBUILD_ZERO_ALLOC` — 74fe2f4c6e
- `DISPATCHER_HARDEN_MUTATION_SURVIVORS` — 7af1251219
- `LIQUIDNET_REBUILD_SHRINK_TO_AFFECTED` — 6793586d4d
- `STEVE_LANE_UNSTICK_PAUSED_UNOWNED_C45B` — efbfbf4872
- `FLEET_RELAUNCH_FIX_ELEVEN_GHOST_TABS` — 894e13620a
- `ACCOUNTPICK_CORRECT_OWNER_PRIORITY` — 52c7a70bd0
- `OPSWATCH_SILENCE_FRESH_WEEK_RUNWAY` — 52c7a70bd0
- `TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME` — 7d6e490b9e
- `OPSWATCH_MONITOR_UNCLAIMED_STEVE_INCIDENTS` — 8b295d809dd2
- `ROLE_CAPS_REMEASURE_ON_REAL_RUNS` — 9953a9cf1d9b
- `ARBITERTRIAL_PROVE_FAKE_CLOSE_FAILS` — 9e68653bbb
- `HELPER_BUDGET_MIGRATE_INTO_DISPATCHER` — bce8d5a772

## Filed and still open (28) — the next seat's queue

- `HOSEOFFLINE_HO7_FIX_STALE_CACHEFRESH_PIN` — validation_hose_offline.py:187 HO7 pins 'HoseLive.CacheFresh(now, portTick, 60)' in CompHoseReel.cs, which uses PhasedFresh since ebf8e5325c: selftest
- `ARTEVAL_INSTALL_DEPLOY_HELD_SWBESTIARY` — Installed art not deployed to src/RimStarWars/SWBestiary: held: ~ Defs/BiomesTeamPort/ThingDefs_Items/RSW_BiomesTeamPort_Items.xml (not a texture); ~ 
- `THIRST_T28_DIAGNOSE_DOUBLE_BLOOD_QUENCH` — Live T28 (SteveDesktop J20261028T183929Z-18e9e8): a Sanguophage's thirst rose 0.2->0.998 after one hemogen pack (+0.8, expected +0.5); pack consumed, 
- `MUTATION_COLLECT_FIX_COPYTO_SILENTLY_EMPTY` — run_mutation collect --copy-to copied nothing for Steve runs 20261028T095621/013440 (summaries had to be scp'd by hand); make it copy or fail loudly
- `WALLREACH_BEGINJOB_TAME_INPUTS_OUT_OF_SLICE` — RM_WallReach: BeginJob/Inputs() reads the whole map and allocates byte[]/Dictionary + new LabelJob inside the timed slice, so the 1 ms slice is unboun
- `HOSE_WATCH_ALLOC_HUNT_GC_IN_TICK` — Hose watch phase: a GC (113-116 ms) landed inside a hose tick in 2 of 4 live windows (HoseEnds:Read; CompHoseReel:Port/HosePorts:Find) after the zero-
- `MINERAL_MATRIX_DESIGN_ROUND_TWO_SPARSER` — Minerals x Baroque Biomes normalization pass: lore-prefilled relative abundance per cell (hand-tunable unit), min/max % mountainous per biome, orthogo
- `STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES` — The SteveDesktop-Runner Claude session commits into ~/rm/runner (the no-LLM dispatcher's pinned clone), which pauses the lane on the next pull/pin (22
- `WARMTIMER_HARDEN_SPARE_LIVE` — claude-account-warm.timer (daily 04:48) warms every account, including the LIVE login when no claude process runs: a refresh of the live credential is
- `SCHEDULEDOC_CORRECT_PRIORITY_RANK` — dispatcher_schedule.json account_pick block still says rank soonest_reset and its _doc describes use-it-or-lose-it; account_pick now ranks by switchin
- `SKILLS_TESTING_POLICY_ABSORB_INTO_CURATION` — Curation session: absorb design/RimMandrake/testing_policy_2026-10-28.md into the testing-related skills (mutation, live-debugging-proof-harness, rimf
- `SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS` — Nightly selftest RED 14/14 nights (75 distinct reds, handoff red 14/14): known-red list after 3 nights, each with an open item, so a new red stands ou
- `SELFTEST_SLOW_FOUR_SHRINK_BY_SPLIT` — 4 selftests at ~600 s (property_fabric, seashores, reclamation_trigger, skeleton_burial) are 41% of nightly test-seconds: split or move to a slow tier
- `TESTQ_FILLER_GUARD_TUNE_LOW_YIELD` — testq filler guard: 247 jobs/27.8 lane-h -> 2 findings (0.07/h) vs fix 2.2/h, sweep 3.5/h; lower testq.fill_hours
- `GPT_CONSULT_MEASURE_COST_UNLOGGED` — GPT consult rounds have no central log and review records carry no consult id: cost/yield per round UNMEASURED
- `WALLREACH_READ_CHURN_TAME_PARTS_MOVED_DROPS` — RM_WallReach: most sliced kinds reads are dropped by ReadPartsMoved before they finish (live RAIN_B2: reads begun/done 1421/211, 1210 dropped; build m
- `V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY` — At the Conductor+Dispatcher+FOUNDRY cutover, every BENCH-owned open item (all FlowWorks and GSS included) is reassigned to the Dispatcher->FOUNDRY que
- `SEAT_SHARD_FIX_UNPUBLISHED_AT_CLOSEOUT` — FOUNDRY's shard sat unpublished 3 h: ringed tickets were ledger-only, close-out step 1 unenforced; fix = dispatcher ring line + seat_restart request r
- `FOUNDRY_SHARD_RESCUE_STRANDED_EVENTS` — Commit + ./publish your FOUNDRY.jsonl: 17 events since 2026-10-28T21:48Z only in /home/mandrake/rm/foundry (clone 87 behind origin); if the push is re
- `AUDITOR_PRESCREEN_FIX_WINDOW_SINCE_LAST_RUN` — Auditor pre_launch screens a fixed last-day window (audit_prescreen.py --days 1): a refused or failed daily run leaves that day's closes never screene
- `BLIND_VIEW_FIX_HIDDEN_HANDUP_HEADERS` — blind_view show prints a note as time/seat/ids only, so the Conductor's allow-list cannot find OPS PROPOSAL / CUT LIST / CUT APPLIED / QUESTION FOR OP
- `AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH` — audit_prescreen.py scored the deliberately fake close ARBITERTRIAL_PROVE_FAKE_CLOSE_FAILS (sha 9e68653bbb) 0 with no flags. Three gaps: (1) evidence_p
- `GLOWTANK_SALT_FIX_ONE_PINCH_ONLY` — FlowWorks broken: glow tank salt draws one unit (GLOWTANK_SALT_DRAWN_ONE_UNIT, GLOW_TANK_LIQUID_FEED_1:A2) - RM_Fluid_BoilingWater, RM_Liquid_BoilingW
- `LIQUID_WAKES_FIX_FOOTPRINTS_GONE_QUIET` — FlowWorks broken: fw_live_checks W1_wakes_terrain_walked fails (2026-10-11) - RM_Fill_Water, RM_SlimeGreen, RM_Tar, liquidWakesEnabled
- `HOSE_SPILL_FIX_OFF_SWITCH_STILL_POURS` — FlowWorks broken: fw_live_checks L5_switched_off_hose_spills and TANK_DEBUG_BUILD_FILL_AT_WILL:A1 fail - RM_Liquid_FreshWater
- `UNIVERSAL_PIPE_FIX_LAST_RULING_STILL_RED` — FlowWorks broken: HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD criterion A5 latest verify not pass - RM_UniversalPipe
- `PIT_ENTRY_PROVE_DONE_BUT_STILL_RED` — FlowWorks broken: WATERED_PIT_FIX_NO_WAY_IN (done) and PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH carry a non-pass latest verify - RM_Ladder, RM_PitRamp
- `GSS_SWITCHES_PROVE_LAST_FOUR_STANDING` — GSS goal 3: prove the four unverified switches with no item (keepWiresOnGravship, cutWiresOnOwnerChange, dripLoops, slideUnder), then re-run proof_all

## Commits

```
b36357d2ce conversations: catch-up 8 record(s)
38c4fe7052 v3 trial night: seat restart on in DRY mode (journals would-SIGTERM only); selftest allows enabled only with dry
60f6a6c96c v3 trial night: enable Arbiter (advisory), Producer, Auditor, Innovator (owner: "I am back at the hotel. Let's get to it!")
d302fbbcea v3 cutover: BENCH lane -> FOUNDRY (V3_CUTOVER_MIGRATE_BENCH_LANE_TO_FOUNDRY)
2c31e9a4a6 ledger: RUNNER ingest of 1 testq job(s)
6c47669c92 dispatcher schedule: caps from first real runs (Producer 800k/1.0M, Auditor 700k/875k); wake cap 6/h, 48/day from measured rings
05f9248133 ledger: RUNNER ingest of 1 testq job(s)
cdf59cb7aa ledger: pending FOUNDRY/OWNER shard events from v3 build helpers
7f27d437cd ledger: Conductor answers Producer's weekly-plan questions
d9a1f93d5b ledger: close HELPER_BUDGET_MIGRATE_INTO_DISPATCHER; note RIMFLOW_V3_BUILD_DISPATCHER_FIRST
79f17cbed2 ledger: Producer trial-ready note (run rm-role-producer-1793234714, 660586 weighted vs cap 500000; enable change stated, not applied)
04125a43ac code review: CLEAN marks for seat_restart.dry + golive set (684f4607ff, 260b83915d)
add83b4a32 golive wave1 doc: Operations' first alarm run is one combined run; Conductor's launch note names no unit (Codex r5 LOWs)
3ca78e4485 ledger: DISPATCHER notes (2)
717596c917 ledger: Auditor/Innovator v3 trial note (Auditor caught HOSE; Innovator refused by RED band)
684f4607ff v3 trial: seat_restart.dry key + go-live set read from the schedule (golive block); runbook dispatcher rows filled
ac4f316835 Producer weekly run 1: 6 items filed for FlowWorks broken parts + GSS switches, verify on 12 plan items, 2 v3 tickets to FOUNDRY
78258a2278 ledger: Arbiter trial results; fixture retired (verify fail); 2 lessons
91e4116d02 ledger: DISPATCHER notes (5)
f2108f5608 ledger: Auditor run rm-role-auditor-1793234714: 4 audits (2 SOUND, 2 DEFECT), file AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH
... 163 more: git log --oneline 1f1cba2dae..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-10-28T23:39:24Z

Working tree clean apart from untracked `Transient/`.

