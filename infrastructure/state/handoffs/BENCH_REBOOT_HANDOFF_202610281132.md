# BENCH_REBOOT_HANDOFF_202610281132 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610280123`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

**The tight live loop works, and it beats the shuttle by hours.** Tonight four "sit on the code and the game" helpers (bridge idle rule, 2-3 h timebox, ≤6 build cycles, all r18 bars re-read at the end) took the excavation/levelling/hose spikes from 134-162 ms to under 20 ms in dry and rain (Levelling dry 134→5.6 ms, HoseLinks 40→1 ms, WallReach rain tail fixed; all 8 r18 bars pass) in ~1 cycle per fix, where r14→r18 via testq had taken a median 94 min per round trip. Two rules make it safe: commit DLL + .srchash + source TOGETHER at every green point (an uncommitted DLL made the pre-push hook refuse every other helper's publish for ~1.5 h), and re-read every bar at the end. This is the Live Fixer (design/RimMandrake/live_fixer_2026-10-28.md) proven by hand on Archmagi.

## What the owner should see

- Briefing mockups v2 (rewritten after your "cryptic and obtuse" + a blind read): phone https://claude.ai/artifact/6QfKGn1jGssoBQ28xmjN63 · desk https://claude.ai/artifact/XrLR3E591Yge2T8KWcQw66 — needs your read.
- Wave 1 today: BlindView is GO (allowlist renderer, GPT GO under the stated accidental-exposure threat model) so the Conductor may join Dispatcher + Operations; every wave-1 Python file except contracts/blind.py is reviewed CLEAN; the Dispatcher's live process scan was blind ~61% of the time under load (fixed 02fff76f38, 0/800 after).
- Foundry fresh-window-per-ticket is built and OFF; turning it on is yours: design/RimMandrake/rimflow_v3_golive_wave1.md §10 (its fallback relaunch via WSL interop is unmeasured).
- CONDUCTOR_SEAT_WIRE_FLEET_FAILOVER needs a window position for a Conductor tile on your screen (I did not invent geometry).
- Your Steven-account ruling is enforced (3bd92c02fc): 48 h after his reset, ≤50%; "48 h" is my reading of "fresh reset" — change it if you meant otherwise.
- Evidence chain cutover 2026-10-30 UTC (6e771b895c, e132148a0d): after it, a crash before a day's first sealed record raises a false tamper alarm a human clears. FOUNDRY's clone is far behind (135 untracked files) — FOUNDRY_CLONE_SYNC_STALE_TIMERS.
- One helper edited design/RimMandrake/flowworks_composite_review_scenarios_2026-10-21.md (two "review-map station only" rows, 5bf1deb85b) without your word; revert if unwanted.
- Mutation scores (measured, SteveDesktop run 20261027T214640): dispatcher 57.9→84.1%, role_launch 66.8→72.4% (bar 85%; new tests projected ~86%, run 20261028T013440 measuring).
- Account: system at ~11% at 22:15; rm-account-failover switches to lukas at ≤2% (deadline 12:45 today).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET` — built, tested, GPT r8 clean, DISABLED behind seat_restart.enabled; NEXT: ask the owner to enable it per golive doc §10 alongside wave 1.
- `HOSE_TICK_REBUILD_ZERO_ALLOC` — rebuilds 15→0 and ~0 alloc shipped (e0a66a89fd), map1 hose still 20 ms dry (periodic recheck) / 30 ms setup (HoseFlow:Signal); NEXT: run a live loop timing the recheck body and Signal, and spread >16384-cell patches over ticks.
- `WALLREACH_VETO_FIX_STALE_FALSE_NO` — fix shipped c9348db9d1, W3 live PASS; NEXT: add a bridge tool to prop a door open and run the W1 live check, then close.
- `LIQUIDNET_SETTLE_FIX_MOVES_ACROSS_CUT_HOSE` — fix shipped c9348db9d1, red-first green; NEXT: stage a drawbridge cutting a hose mid-settle on the test save and run the live check, then close.
- `ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS` — new tests published, projected ~86%; NEXT: collect SteveDesktop run 20261028T013440 (status/collect cmd on the item) and close if role_launch ≥ 85%.
- `BLIND_REVIEW_FINISH_ROUND_NINE` — contracts/blind.py findings classified (deliberate case rule; withheld-count undercount on 0/False paths, no leak); NEXT: fix the undercount red-first, one review round, mark clean.
- `TESTQ_INGEST_REVIEW_FINISH_ROUND_FOUR` — one bug fixed dcabaa2252; NEXT: one more full-file review of Utils/testq/ingest.py and mark clean if empty.
- `LIVE_FIXER_DESIGN_ONE_SEAT_NO_SHUTTLE` — design + owner rulings propagated (36fab8cb72); NEXT: build the Steve-side Fixer mode (start with WINBUILD_DOTNET_MIGRATE_STEVEDESKTOP_PATH).
- `CONDUCTOR_BRIEFING_DESIGN_ONE_PAGE_NOT_SIX` — v2 mockups published; NEXT: get the owner's read, then build briefing.py from the doc.

## Traps learned

- An uncommitted FlowWorks DLL/.srchash in the shared clone makes the pre-push hook refuse every other helper's ./publish (filed: lessons 20261028T113321Z).
- Hand-applying mutants: match by line number and avoid stale .pyc (filed: lessons 20261028T064946Z).
- A mutated __main__ guard makes a script selftest exit 0 before any assert (filed: lessons 20261028T070943Z).
- Dispatcher selftests read the bench clone path, so off-Archmagi mutation runs tested the wrong copy (filed: lessons 20261028T044846Z).
- GC.GetTotalMemory deltas are not a tick's allocation (filed: lessons 20261028T075638Z).
- GPT asked "can a blind role EVER see…" invents adversarial routes forever; state the threat model in the ask (filed: lessons 20261028T113321Z).

## Closed since the last handoff (35)

- `STEPPULSE_SHRINK_STEADY_SLICE_COST` — b1cc4c3409
- `MUTANTS_HUNT_ON_IDLE_STEVE` — 88e2214ea23c52b9e008f91679a3bf8cfd0c48f3
- `THIRST_ROWS_HARDEN_FALSE_PASS_ROUTES` — 63eddf054a12
- `BLINDVIEW_FIX_TOKEN_WORD_FALSE_WITHHOLDS` — 24c9e6f4e583
- `BLINDVIEW_HARDEN_SIX_LEAKS_STILL_OPEN` — c78d5406a525
- `CAST_ROSTERS_RESTORE_CUT_XENOTYPE_RACES` — 7ff41aacf751
- `FLOWWORKS_RAIN_SETTING_CALLSITES_FIX_DRIFT` — bdf66fc6439b
- `SCENARIOS_MAP_FIX_LADDER_ICE_NO_HOME` — 5bf1deb85bc9
- `RIMPULSE_AGENTS_BUILD_DAY_TIMELINE` — 5cc700c339bd
- `PIPE_SEAT_ELBOW_FIX_VS_SELFTEST_CONSTANT` — 796a9f22158f
- `ART_REFERENCE_TEXTURE_CHECK_FIX_SHA_OVERLAP` — 249c82c0a43c
- `ROLE_LAUNCH_HARDEN_MUTATION_SURVIVORS` — d63ac0da65b4
- `ARBITER_VERDICT_WIRE_JSON_SCHEMA_HANDOFF` — 2bb25707ac86
- `DISPATCHER_SELFTESTS_HARDEN_HARDWIRED_CLONE` — 6e2d2d66d2
- `TESTQ_OUTCOME_HARDEN_TAG_ONLY_KEYERROR` — a6cdd76847f2
- `TESTQ_HARDEN_RECONCILE_NONDICT_CRASH` — a6cdd76847f2
- `TESTQ_SCHEMA_RECONCILE_UNDECLARED_MARKERS` — a6cdd76847f2
- `TESTQ_ALLOWANCE_HARDEN_TOO_WIDE_A_GATE` — 147d0b7d09
- `SELFTEST_EVIDENCE_FIX_COVERS_TESTS_ONLY` — 4af114b7945e51f67102c28bd35e1ed3d5087ec7
- `LEDGER_TS_HARDEN_NONISO_AFTER_CUTOFF` — 3a4f0a3089
- `AUDITS_SHA_HARDEN_TRAILING_NEWLINE_MATCH` — 3a4f0a3089
- `DISPATCHER_JOURNAL_TAME_REPEAT_TS_SKIPS` — 7e10cc2e03
- `HOSELINKS_REFRESH_DIAGNOSE_MAP0_TICK_SPIKE` — ebf8e5325c73
- `ROLE_LAUNCH_REVIEW_FINISH_ROUND_FIVE` — 5efb1ce5f9
- `EVIDENCE_SEALS_HARDEN_STRIPPED_LOOKS_DELETED` — 6e771b895cd6
- `BLIND_REFS_WIDEN_SHORT_SHA_HIDDEN` — 008f02a161
- `WALLREACH_BUILD_DIAGNOSE_RAIN_TAIL` — 45ac3920e6c0
- `SELFTEST_A2_SOURCE_FIX_STALE_PATTERN` — 45ac3920e6c0
- `ROLE_EVENT_KEY_WIDEN_SAME_SECOND_TWINS` — abe94adc6352
- `EVIDENCE_CUTOVER_CLONES_SYNC_CHECK` — e132148a0d02
- `EVIDENCE_SELFTEST_FIX_WRITES_REAL_STORE` — 04d7610eb0
- `PROCS_SELFTEST_FIX_LIVE_PROC_FLAKE` — 02fff76f38b9
- `OPS_SILENT_FLAG_FIX_OUTLIVES_SERIES` — 02fff76f38b9
- `ROLE_LAUNCH_REVIEW_FINISH_ROUND_EIGHT` — dcabaa2252eb
- `POCKETRAIN_FIX_SURPLUS_CROSSES_SLUICE` — 07dcaa2ada

## Filed and still open (30) — the next seat's queue

- `LIVE_FIXER_DESIGN_ONE_SEAT_NO_SHUTTLE` — rimflow v3 has no owner for a tight live fix loop: one agent holds one ticket plus a test-rig lease (SteveDesktop or Archmagi game) and iterates edit-
- `THIRST_STORE_TANK_DIAGNOSE_LATE_BRINE` — FlowWorks thirst T23: after a Fill tank is switched to Store, 1 brine bucket lands in the 900-tick settle though the worker was on GotoWander at the s
- `CONDUCTOR_BRIEFING_DESIGN_ONE_PAGE_NOT_SIX` — Conductor briefing: one templated, beautiful report that brings the owner up to speed, keyed to since-you-last-read: asks first (questions, review art
- `CLOSE_EVIDENCE_HARDEN_MUTATION_SURVIVORS` — close_evidence.py: 460 of 1130 mutants survive selftest_close_evidence (score 58.9%, 5 timeouts); add red-first tests for _main/_ship_to_wsl/_bad_mark
- `DISPATCHER_HARDEN_MUTATION_SURVIVORS` — dispatcher.py: 872 of 2071 mutants survive selftest_dispatcher+_r2 (score 57.9%, 6 timeouts); add red-first tests for execute/decide.one_seat/decide/a
- `LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE` — RM_Levelling.Tick (100 rigs, map1 325x325) max 134.4 ms in the r18 dry steady window and 161.8 ms in the first 1000 ticks after load (r17 dry max 12.9
- `SHEETRAIN_DOPULSE_TAME_DELUGE_SPIKE` — With sheet overflow ON (it ships OFF), a pocket-rain deluge (rainFillPerPulse=1, 2000 ticks) put RM_MapComponent_Excavation max at 35.2 ms: DoPulse ma
- `CONDUCTOR_GOODBYE_DESIGN_FRESH_EACH_TIME` — Conductor quick-mode lifecycle: the owner's goodbye triggers a close-out, then the Dispatcher kills the window and relaunches a fresh Remote Control C
- `STEVE_WORKER_HARDEN_GUARD_RACE_REQUEUE` — worker.py checks the game guard at cmd_start (line ~266) but a holder appearing before Attempt.run makes a terminal REFUSED/GUARD_HELD (line ~733) ins
- `WINBUILD_DOTNET_MIGRATE_STEVEDESKTOP_PATH` — winbuild.py hardcodes C:\Users\Mandrake\.dotnet\dotnet.exe and the /mnt/d/ClaudeWork build root; SteveDesktop has .NET SDK 8 from winget under another
- `OWNER_WAITS_DRAIN_28_ANSWERED_NOT_MOVED` — Pulse digest says 0 new asks while 49 owner items wait (39 >3d); 28 look already answered in his words but never moved. List: D:\ClaudeWork\rimmandrak
- `PULSE_HANDS_RETIRE_THIRTEEN_HELD_FOREVER` — RimPulse holds 15 looks, 13 of them stale hands that never retire; they crowd the page every day. Retire rule proposed in conductor_briefing_2026-10-2
- `FOUNDRY_CONTEXT_BUILD_FRESH_PER_TICKET` — Foundry's long-lived window accumulates stale context across tickets (the same failure the Conductor goodbye restart solves). Build: after each ticket
- `ARTPIPE_IDLE_FILL_EMPTY_ALL_NIGHT` — Art queue sat empty the whole night of 10-26/27 (0 waiting, 0 running, last output 10-26 12:51 PDT) while Surrik s2 and the Durrok/Mullgoth redraws we
- `RIMPULSE_LEDGER_TAME_TAIL_READ` — RimPulse /agents re-reads every ledger shard whole on each change (agents_timeline.read_ledger_bits); parse only appended bytes and keep a bounded tit
- `ART_SHEETS_REBUILD_FOR_REFERENCE_PANELS` — rebuild drawbridge_art_sheet_2026-10-20 and the three br1e bore sheets so their scale carries refs panels
- `SELFTEST_UNMEASURED_FOUR_REBUILD_DEFDUMP_DB` — 4 UNMEASURED selftests need a fresh DefDump capture + measure build (stale/absent defs.sqlite, dump blind to xenotypeSets)
- `CONDUCTOR_SEAT_WIRE_FLEET_FAILOVER` — Add CONDUCTOR to install_wt_seat_profiles SEATS and launch_fleet.ps1 place/titleFor (geometry needs owner), then append ,CONDUCTOR to -Seats in ~/.cla
- `ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS` — role_launch.py: kill the decide_roles.one / _supervise_one / after_ready / _signal_marked mutation survivors left after selftest_role_launch (d63ac0da
- `SLOT_OVERAGE_REMEASURE_BY_HELPER_MINUTES` — slot_allocator _overage samples helpers_running once per 15-min check and applies it to the whole interval: helper batches that start and finish betwe
- `ACCOUNT_FAILOVER_RETIRE_AFTER_DEADLINE` — Retire account_failover.py + rm-account-failover.timer after its 2026-10-28 12:45 deadline
- `HOSES_MAP1_DIAGNOSE_TICK_STALLS` — RM_MapComponent_Hoses on map1 (BENCH_r17_midrain) costs 0.6-1.7 ms/tick with single-tick max 100-187 ms per window (c1 DRY 101, A2 187, B2 187); HoseL
- `BLIND_REVIEW_FINISH_ROUND_NINE` — contracts/blind.py still DIRTY after review r6-r8 (stop rule): every round's findings were fixed red-first (cec500333f, 72f06c404b, 2161464c77) but no
- `HOSE_TICK_REBUILD_ZERO_ALLOC` — Hose tick: pooled CordPlanner A* + CordWorld dirty-cell patching so the hose tick stops drawing 120-140 ms full GCs (3/53 GCs landed in hose ticks) an
- `TESTQ_INGEST_REVIEW_FINISH_ROUND_FOUR` — src/RimMandrake/Utils/testq/ingest.py still DIRTY after full-file review r1-r3 (stop rule): every real finding was fixed red-first (97bf763248, publis
- `FOUNDRY_CLONE_SYNC_STALE_TIMERS` — /home/mandrake/rm/foundry sits at c837e3ddb1 (no close_evidence.py, 135 untracked) while rm-codebase-health and rm-mirror timers run code from it. Whe
- `SURFACEGAP_MERGE_ARMS_THROUGH_POND` — RM_SurfaceGap.Measure (RM_LevelSolve.cs:603-622) and its twin level_water.surface_gaps measure each 4-way dug run against a joined pond separately and
- `WALLREACH_VETO_FIX_STALE_FALSE_NO` — RM_WallReach veto can answer a false NO from stale state: W1 KindOfDoor ignores Building_Door.FreePassage (door propped by item/pawn reads shut for Pl
- `LIQUIDNET_SETTLE_FIX_MOVES_ACROSS_CUT_HOSE` — RM_LiquidNet SettleTick/DumpDrain move liquid across a hose cut earlier in the same tick: RM_HoseLinks.Refresh is cached per tick (checkedTick), hose 
- `FLOWPINS_FIX_PASS_ON_REGRESSION` — FlowWorks SelfTest source pins that pass on the regression they claim to catch (GPT cs_review job consult-20261028-023921-127363)

## Commits

```
d7cf6a1c03 conversations: catch-up 2 record(s)
18aab6b259 ledger: bridge release after cs_review apply
25af3e550e FlowWorks walk: cs_review live lessons (W3 false NO observable paused, W2 sub-frame, bar 3 A2 noise ruled out); ledger notes, W1 and LiquidNet live checks still owed
28d23aa23c ledger: RUNNER ingest of 0 testq job(s)
c9348db9d1 FlowWorks: wall-reach veto drops stale false NOs (item-propped door, pending breach, off/on, mid-load kinds); liquid settle and dump check the hose route before moving (cs_review 2026-10-28)
bb1034ea1f v3_vs_v2: mutation-survivor tests for classify/judge_week/standing/reference/settled (V3_VS_V2_HARDEN_MUTATION_SURVIVORS, note)
5757dff4ed ledger: game-state stamps
08dfaa7906 ledger: hose loop note
fc3b503694 FlowWorks walk: hose zero-alloc lessons (swim folds, overflow builds, heap-growth control, remaining >10 ms sources)
dceae73af0 ledger: RUNNER ingest of 0 testq job(s)
e0a66a89fd hose world: swim publishes patch their squares, not a whole rebuild (HOSE_TICK_REBUILD_ZERO_ALLOC, in progress)
d60d7cb50a FlowWorks SelfTest: PitAccess arrival-detector pin counted one detector twice (cs_review, FLOWPINS_FIX_PASS_ON_REGRESSION); review records and ledger
b46fb6229c FlowWorks RM_RainPass: Step's doc summary sat on HoldsPulse (two summaries there, none on Step) (cs_review)
924058a1b9 FlowWorks levelling: drop the stale duplicate doc summary on DugBody (cs_review)
cd0b3cd301 Rebuild RimMandrakeFlowWorks.dll from committed source at landing
75448571bb hose world patched cell by cell, not rebuilt whole (HOSE_TICK_REBUILD_ZERO_ALLOC, in progress)
61f7b311d1 role_launch: red-first golden mutation-kill selftest for decide_roles/_supervise_one/after_ready survivors (ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS); wired into run_mutation.py; ledger note
5a7990d72d FlowWorks SelfTest: the level-run walk check holds the queue to the old walk square for square, in order (a set test let a duplicate or reordering pass)
07dcaa2ada FlowWorks kernel: pocket rain keeps each run's surplus behind a shut sluice, a sealed square takes its part-notch of rain, a dry square skips a switched-off source (POCKETRAIN_FIX_SURPLUS_CROSSES_SLUICE)
c96379add3 mutation: delegated_digest shard clones get src (its selftest scans repo XML for the def registry); ledger: notes on mutation run 20261027T214640 scores and re-run 20261028T013440
... 206 more: git log --oneline 672c040a0d..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : LOADING  → corrected to UP, measured now
- Bridge: FREE    since 2026-10-28T11:32:06Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M infrastructure/state/ledger/events/OWNER.jsonl   BENCH helpers' game-state stamps; committed with this handoff
```

