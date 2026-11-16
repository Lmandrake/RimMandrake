# Pipeline sleepers census, 2026-11-15

Item `RIMMANDRAKE_SCAN_PIPELINE_SLEEPER_TICKETS_ANYWHERE_THEY_HIDE`, a detached run from 5:25 to about 6:10 PM PST.
Owner, 2026-11-15: *"No more sleeper tickets. I also want you to scan for other sleeper tickets for the Pipeline like
this too. SCAN THEM ALL, anywhere they might be hiding."*

A **sleeper** is decided, specified or promised work on the pipeline's own machinery that nobody is working and nothing
will launch. Mod and game content are out of scope. The known positives, used to prove each instrument could see, are
the three preflight tickets of `design/specs/2026-11-12-ticket-preflight-before-any-token.md` §7.

**What launches anything today** `[measured]`: only `maturation_dispatch.py` (mod stage runs) and `red_dispatch.py`
(nightly reds, held since 16:33 PST by the owner's nightly-hold card). Every other open item waits for the Conductor to
launch a helper. So every open pipeline item that is not `doing` is a sleeper unless the Conductor picks it.

## 1. Counts per hiding place, and the probe that proved the instrument saw

| Place | Read | Found | Probe that the instrument sees |
|---|---|---|---|
| Ledger, open items | 2,195 open (all seats), replayed through `model.replay` | ~650 pipeline by title; 560 still open after this run (316 proposed, 162 ready, 65 built, 11 validated, 6 doing); 261 idle 7+ days | the three preflight tickets classify as pipeline (title and prose classifiers both) |
| Ledger, blocked items | 398 open blocked | **46 blocked with kind `judge` by a Relentless snag**: the judge retired with Relentless, so nothing will ever lift them; most say their work already landed | `ARENA_TRIAL_RETIRE_HUNDRED_GIGS_IDLE`: landed 1f0e666566dc, L0 pass recorded, blocked since 11-06 |
| Specs and plans | 669 design files; item-shaped names in backticks checked against the ledger | 2 names never filed (preflight tickets 4 and 5); plan slices 2b and 3 with no item | the 2 unfiled names are the preflight spec's tickets 4 and 5 |
| Handoffs since 11-01 | 55 files, 804 `NEXT` lines, 494 distinct ids | 236 open (covered by the ledger read), 240 closed, 18 ids never filed: all retired-loop, arena or FOUNDRY work, or done | the template lines are the only id-less NEXT lines of 11-13..11-15 |
| Conductor log | 3,983 lines, 553 `RAISE FIRST`, 7 `LEFT OPEN` | "file an item and cut its cost now" printed 10 times for the Designer with no item ever filed; 4 duplicate Operations-overrun items | the Operations overrun raises map to 4 existing items |
| Detached-run results | 306 `*.out.json` in `D:\ClaudeWork\rimmandrake\dispatcher\detached\` | 22 name owed or follow-up work: 10 on items still doing, 1 proposed, 11 on closed items; the 3 closed pipeline ones were read, and each follow-up is filed or landed | the GSS cycle-3 result's "a new blind judge is owed" maps to the filed cycle-4 item |
| Incidents | 14 open | 4 plans whose "Next: the Conductor launches ..." never launched (dispatcher, Steve HAR, nightly r2, Designer chain) | `maturation-20261115141356`'s named item was launched and is done |
| Stranded work | 267 orphan bundles, 11 parked-dirt dirs, pool report | 1 pipeline bundle with unlanded code (the Designer-draft run of 00:49Z; its second run re-landed it as 9a000f9246); 113-head "unpushed" bundles are archive tags only; parked dirt is stage.json/ledger/conversation leftovers | `git apply --reverse --check` reads 2 landed patches as landed |
| Lessons, findings, hands, owner queue | 381 lesson files (all newer than 11-08); findings fold; `maturation_hands.py list`; `owner_queue.py` | lessons: covered by `LESSONS_BACKLOG_DRAIN_SINCE_SEPTEMBER`; findings "failed again" pile is 5 mod rows; 1 open hand act; 15 owner-answered items whose next move is ours (6 pipeline) | owner queue lists the items he answered by card |
| Conversations, last 7 days | 427 records, 429 owner turns, 131 pipeline instructions | 87 with no owner-quote match on the ledger; read by hand, every pipeline one traced maps to an item or a landed commit (the judge's exact image: ed99e8360629; restarts: E1..E4 filed 01:46Z); one not traced: 11-15 13:04 "update the codex account info on fleet now sheet" | the preflight order (11-12, "check the tickets deterministically first") is in the unmatched set yet filed in agent words: the matcher is an upper bound |

## 2. Live sleepers, ranked

Ranked against `design/specs/2026-11-15-cheap-guards-at-every-door.md` §9, whose nine tickets (landed 01:43Z) come
first by measured waste and are the Conductor's #1 priority by the owner's order; they are not sleepers. Its order puts
the preflight trio after its nine. The list below is what sits outside that order, by waste it stops or work it frees.

| # | Item | Why it is a sleeper | Waste it stops / work it frees |
|---|---|---|---|
| 1 | `RIMMANDRAKE_FIT_DISPATCH_TICK_IN_ITS_BEAT` | Filed 11-14. Incident `dispatcher-20261115150613` is at **emergency**; its plan says "the Conductor launches one rm-fixer (sonnet)", never launched | 25 of 608 Dispatcher beats killed in 24 h; `publish:stuck` raised 7 times on 11-15 |
| 2 | `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` (filed here) | 45 items blocked on a judge that retired with Relentless 2026-11-13 | Frees 45 items; most are landed work that only needs a plain-shell proof run and a close |
| 3 | The preflight trio: `RIMMANDRAKE_BUILD_PREFLIGHT_SPINE_TIMED_FROM_BIRTH` -> `RIMMANDRAKE_EXTEND_PREFLIGHT_CORE_KINDS_IDS_SHAS_FULL_REASON` -> `RIMMANDRAKE_BACKTEST_PREFLIGHT_OVER_REAL_PAST_TICKETS` | Filed 11-13 00:25 PST with acceptance tests, never claimed; tickets 4 and 5 unfiled by design (the guard spec now owns their door) | Upper bound 12.5% of mapped spend in the measured week; the saving on top of today's gates is UNMEASURED (ticket 3 measures it) |
| 4 | `RIMMANDRAKE_CUT_DESIGNER_RUN_COST_TEN_RAISES_NO_ITEM` (filed here) | 10 "file an item" raises in the Conductor log, none filed; incident `roles-20261115093955` (Contagion chained 8 times) plan never launched | Linked to the guard spec's stage-order decision `RIMMANDRAKE_DECIDE_COVERAGE_LOOK_BEFORE_EXAM_SIX_EXAMS_RETAKEN` (USD 18.79 of exam retakes) |
| 5 | `RIMMANDRAKE_DIAGNOSE_OPS_RUNS_OVER_BUDGET_FOUR_OF_ELEVEN` | Now the single survivor of four duplicates (three superseded here); 36 Conductor-log raises on Operations' spend | 4 of 11 Operations runs over budget in 7 days |
| 6 | Refusal-contract remainder: `RIMMANDRAKE_BUILD_NEUTRAL_CRITERIA_FIXER_WITH_GUARD` (auto-launch and fresh rejudge owed since 57b99e45ff, 11-13), `RIMMANDRAKE_RECORD_GATE_REFUSALS_DROP_DEAD_MARKER` (T3; `evidence_gate.py` is read by `rimflow close`, so it is live), `RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS` (T7), parent `RIMMANDRAKE_BIND_REFUSALS_TO_FIXES_NO_CEREMONY_LOOPS` | The 11-13 run stopped with these owed; nothing relaunched it | A judge's "criteria suspect" still reaches no fixer by itself |
| 7 | `RIMMANDRAKE_DRAIN_LIVE_RUNS_BEFORE_ACCOUNT_SWITCH_NOT_AFTER`, `RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT` | Filed 11-15, unclaimed | Runs killed mid-work at each switch; the guard spec lists 7 kill-and-relaunch pairs as UNMEASURED |
| 8 | `RIMMANDRAKE_HOLD_DET_CLONE_UNTIL_RETURNED` | 410d70d8ea (11-14) appears to implement it; never verified or closed; two duplicates superseded into it here | Cheap: one selftest run at that sha and a close |
| 9 | `RIMMANDRAKE_DIAGNOSE_HAR_CTOR_TOKEN_ZERO`, `RIMMANDRAKE_FIX_DISPATCHER_R2_GREEN_BY_HAND_RED_NIGHTLY` | Each is the named fix of an open incident (`steve-20261115005132`, `testing-20261101162433`) whose launch never happened | Each bad Steve job burns ~10 min of the lane; r2 matters less while the nightly is held |
| 10 | `RIMMANDRAKE_SET_CONDUCTOR_WINDOW_TO_FABLE_POLICY_ALREADY_SAID` | The owner asked 11-13 ("There must be a way to make that default"); proposed since | Every restarted Conductor window comes up on the wrong model |
| 11 | Wrap-up debris trio: `RIMMANDRAKE_WRAPUP_CARRY_LIVE_HELPER_CLONES_NOT_DEBRIS`, `RIMMANDRAKE_SKIP_WRAPUP_ROWS_A_LIVE_UNIT_CARRIES`, `RIMMANDRAKE_EXEMPT_QUEUE_PROJECTIONS_FROM_DEBRIS_EVERY_HELPER` | Three overlapping items, incident `wrapup-20261113102602` open | False debris alarms on every helper run; one build covers all three |
| 12 | Owner-answered, ours to move: `RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING`, `DELEGATED_CARDS_FIX_HELD_OUT_RECALL` (two duplicates superseded into it) | `owner_queue.py`: answered, next move ours | Alerts that ring; a hook red since 10-26 |
| 13 | Full-file reviews owed on DIRTY pipeline code: `RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM` (ops_watch.py and others), `FOUNDRY_RETIRE_REVIEW_DIRTY_FILES` (cli.py and others), `HANDOFF_RESTART_AUDIT_FILES_OWED`, `CLEANER_SANITY_REVIEW_FINISH_FULL_FILES` | None claimed; the last sits in the owner's "truly his" list though a review is ours (misrouted) | Pipeline code nobody has read whole |
| 14 | `RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES` (plan parent, slices 1, 2a and 4 built, never claimed) and `RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` (filed here: slice 2b, no measured incident yet) | Plan work outside the guard order | An `advance` refused again and again counts nowhere |

**The tail.** 560 open pipeline items remain; 261 have had no event for 7+ days, 71 of those with no owner words at
all (many others carry only the 11-02 FOUNDRY-retirement card stamped on them). They are mostly rimflow-v3,
slot-allocator, account, scratch-reap and seat-restart work of 10-23..11-07. This run did not probe them one by one; the
whole list with state, age and idle days is `design/RimMandrake/pipeline_sleepers_census_2026-11-15.tsv`. A stale-drop
sweep of that tail (one probe each, per the CHARTER's stale default) is the next step, and is not filed: it is this
item's own remainder.

## 3. Ended by this run (106 items, each with its proof in `--reason`, plus one of its own filings withdrawn)

- **73 dropped: Relentless machinery** (Relentless Agent steps RA_S03..S18, the RELENTLESS_* tick/exam/Marker/store
  items, the off-tick rewires, bind-judge, wall, self-build, its alarms and pages). Proof: retired by the owner
  2026-11-13, nothing to resume (`design/RimMandrake/retired_loops_2026-11-13.md`; `rm-relentless.timer` in
  `src/RimMandrake/rimflow/live_retired.txt`). Kept, because they are live: `RIMMANDRAKE_RECORD_GATE_REFUSALS_DROP_DEAD_MARKER`
  (`evidence_gate.py` is read by `rimflow close`) and `PROOFLINT_FIX_ARGS_READ_AS_SCRIPTS` (`relentless_live.py` is still
  imported by live proofs). `RA_S17_TRUST_MEASURE_NUMBERS_FOR_HIM` was dropped by a diagnostic call with the reason "x";
  a note on it carries the real reason.
- **7 dropped: RimPulse and Fleet Watch** (retired 2026-11-03 and by `FLEETWATCH_CODE_RETIRE_NOBODY_WAS_WATCHING`; no
  rm-pulse or rm-fleetwatch timer exists), including the two `LIVE_RESTORE_RM_PULSE_*` promises.
- **5 dropped: FOUNDRY's own window, rings and cutover audit** (seat retired by card 2026-11-02).
- **4 dropped: Artisan and Whittle comparisons and redesigns** (loops retired 2026-11-13).
- **6 dropped: stale alarms**: `OPS_TIMER_REPAIR_EC51`, `OPS_TIMER_REPAIR_PRXC` (no failed unit now),
  `OPS_TIMERS_REVIVE` (rm-red-dispatch is held on purpose, `timers_guard.py run` says so), three arena-selftest reds (the
  selftests were deleted in 1f0e666566).
- **11 superseded as duplicates**: 3 Operations-overrun items into `RIMMANDRAKE_DIAGNOSE_OPS_RUNS_OVER_BUDGET_FOUR_OF_ELEVEN`;
  2 scratch-dirt alarms into `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ`; 2 old Steve INVALID streaks into
  `OPS_STEVE_DIAGNOSE_INVALID_SHARE_UKDG`; 2 det-clone items into `RIMMANDRAKE_HOLD_DET_CLONE_UNTIL_RETURNED`; 2
  delegated-cards reds into `DELEGATED_CARDS_FIX_HELD_OUT_RECALL`.

Filed: `RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED` (acceptance test
`src/RimMandrake/rimflow/acceptance/judge_blocked_drained_accept.py`, watched failing: 45 listed),
`RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS` (the plan's test passes on base, so none yet, with the reason),
`RIMMANDRAKE_CUT_DESIGNER_RUN_COST_TEN_RAISES_NO_ITEM` (none: cause undiagnosed). `RIMMANDRAKE_BUILD_COMMON_MOD_PREFLIGHT_ONE_ROW_FORMAT`
was filed and withdrawn within the hour: the cheap-guards spec measured no waste at that door and rejects a new stage
preflight framework.

## 4. Hiding places that should not exist (work written where no queue reads)

1. **A block whose lifter is retired.** 46 items blocked with kind `judge` on Relentless's binding-repair judge. `rimflow`
   lets a block name a lifter that no longer runs, and `next` never offers a blocked item, so done work hid there.
2. **Incident plans.** "Next: the Conductor launches ..." is written into an incident, which no launcher reads; four
   such launches never happened. An incident's Next should be an item (or a launch) at the moment it is written.
3. **Conductor-log "file an item" raises.** The log tells a reader to file; if the reader does not, the order lives only
   in a log that already holds 553 raises. The raise itself should file (one fixed id per kind, as alarms do).
4. **Spec and plan tables of tickets.** Slices and "ticket N" rows marked "proposed" sit in a spec with no item; only a
   name in backticks is checkable. The specnames check of section 1 (names in specs that the ledger never saw) is cheap
   enough to run at publish.
5. **Orphan bundles.** `/home/mandrake/rm/relentless/store/orphans/bundles/` (267) holds the unlanded work of dead
   runs, announced once in a ledger note; nothing lists the ones still unlanded. The `real.patch` / `real_untracked.tar`
   / `commits.bundle` triple is readable by program (section 1's probe).
6. **`.git/rm-dirty-parked` in the bench clone.** 11 parked-dirt folders from 11-05..11-15 that no tool reads back.
7. **Retired code's selftests.** 118 `selftest_relentless*.py` remain; the clone pool refused 8 clone calls today at cap 0,
   the last with purpose `relentless I0` from a `selftest_relentless.py` fixture (`~/.local/state/rm-objstore/uses.jsonl`).
8. **Owner-answered items whose move is ours**, readable only through `owner_queue.py`: 15 sit answered, one review item
   is routed to him by mistake.

## 5. Not scanned (UNMEASURED)

- The 560 remaining open pipeline items were classified by title and read in bulk, not probed one by one; which of the
  261 idle 7+ days are dead is UNMEASURED.
- The regex title classifier's miss rate on pipeline items filed under mod-sounding names is UNMEASURED (the two
  classifiers agreed on every known positive).
- Detached-run result files: scanned by pattern only ("not built", "owed", "follow-up", "LEFT OPEN" ...); a result
  that names owed work in other words is UNMEASURED.
- `situation_*.md` and report files beside the Conductor log (5 situation files, 219 entries): not read.
- Lessons (381 files): counted, not read for un-ticketed pipeline work.
- Handoffs older than 2026-11-01 and conversations older than 2026-11-08.
- SteveDesktop's clones, stores and scratch: not reached.
