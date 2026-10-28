# BENCH_REBOOT_HANDOFF_202610281706 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202610281132`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**Written BEFORE the account switch (system→lukas, expected ~10:50 PDT) that closes every Claude window; helpers running at that moment die, and only what they published survives.** The owner's order (2026-10-28 09:40): *"Ok, wake up! We have tokens to burn! Use up this account, then switch to the other account and use it up to 2% to, then wait for the reset to hit."* account_failover.py (rm-account-failover transient timer, every 5 min) does the switch and stage 2 itself: BURN n 16 on lukas until 15:59, DARK (both seats 0) once lukas ≤2%. So after the relaunch: keep ~16 helpers busy on lukas until stage 2 says DARK, then spawn nothing until lukas resets 16:00. Re-spawn every helper listed below whose work did not publish.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- History rewrite (RIMMANDRAKE_EXCISE_WORK_HISTORY): the Mac laptop's 05:04 cutover attempt paused every rm-*/testq-* timer and never resumed or cut over; BENCH restarted timers 09:41. Owner by card 09:55: **"Tonight, overnight"**. Tonight's night shift must be held off for it; ticket D:\Luke\dev\RimMandrake\tickets\RIMMANDRAKE_EXCISE_WORK_HISTORY.md says how.
- GPT deep research on hose/wire algorithms (owner asked 09:5x): report path D:\Luke\dev\RimMandrake\design\RimMandrake\hose_wire_algorithms_advisory_2026-10-28.md (partial if the switch killed the helper).
- claude-account `use` had never run live on Archmagi; its --dry-run passed 10:05 from outside Claude (arm → dry-run → disarm; machine left DISARMED, the failover arms it itself).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `HOSE_TICK_REBUILD_ZERO_ALLOC` — live-loop helper (opus, bridge held) started 09:42; NEXT: check `rimflow bridge who` and release a dead hold, read the item's notes, re-spawn the live loop if not closed.
- `HOSE_WIRE_ADVISORY_GPT_DEEP_RESEARCH` (no item; owner request) — opus helper started ~09:57; NEXT: if design/RimMandrake/hose_wire_algorithms_advisory_2026-10-28.md is missing or partial, re-spawn it from the research folder /mnt/d/ClaudeWork/rimmandrake/research/hose_wire_2026-10-28/ and finish.
- `SURFACEGAP_MERGE_ARMS_THROUGH_POND` — opus helper started 09:42; NEXT: read the item and git log, re-spawn if not closed.
- `FLOWPINS_FIX_PASS_ON_REGRESSION` — sonnet helper started 09:42; NEXT: read the item, re-spawn if not closed.
- `ARTPIPE_IDLE_FILL_EMPTY_ALL_NIGHT` — helper committed dce017d62b (idle_fill timer); NEXT: confirm it is pushed and the item closed, else finish.
- `TESTQ_INGEST_REVIEW_FINISH_ROUND_FOUR` — r5 fixes pushed d7bf479a17; r6 --git-dir lock finding being fixed; NEXT: if not clean, fix the r6 finding red-first and run one more round.
- `SLOT_ALLOCATOR_REVIEW` (no item) — round 1 fixed 3 bugs f67097d77f but wrongly marked clean; round 2 running; NEXT: run round 2 if not published, fix SLOT_BURNACCOUNT_FIX_DORMANT_TIE too.
- `ACCOUNT_FAILOVER_RETIRE_AFTER_DEADLINE` — account_failover.py r4 7efbfd3db7, still DIRTY; NEXT: after 16:00 PDT, retire the transient timer (`systemctl --user stop rm-account-failover.timer`) and close the item.
- `DISPATCHER_HARDEN_MUTATION_SURVIVORS` / `CLOSE_EVIDENCE_HARDEN_MUTATION_SURVIVORS` / `ROLE_LAUNCH_KILL_DECIDE_ROLES_SURVIVORS` — Steve runs 20261028T095621 (dispatcher) and 20261028T013440 (close_evidence) mutating; role_launch 73.2% needs a fresh run; NEXT: collect per the item notes, start the role_launch run, close what reaches 85%.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- An agent that pauses timers must arm their restart in the same command; the 05:04 pause stopped the deadman too, so nothing alarmed for 4.6 h (see: TIMERS_DIAGNOSE_SILENT_MASS_STOP).
- Parsing a subprocess's output after tail-truncating it for the log made account_failover blind to the live account (filed: lessons 20261028T164801Z).

## Closed since the last handoff (3)

- `RIMPULSE_LEDGER_TAME_TAIL_READ` — 8d1493eb60b8
- `BLIND_REVIEW_FINISH_ROUND_NINE` — a11ea24368
- `SLOT_OVERAGE_REMEASURE_BY_HELPER_MINUTES` — 099b5faa1e28

## Filed and still open (2) — the next seat's queue

- `TIMERS_DIAGNOSE_SILENT_MASS_STOP` — Every rm-* and testq-* systemd user timer on Archmagi (plus the transient rm-account-failover timer) was Stopped at 2026-10-28 05:04:39 PDT with no ta
- `SLOT_BURNACCOUNT_FIX_DORMANT_TIE` — slot_allocator pick_burn_account: every account polled in one sweep shares measured_at, so max() ties and picks the first dict key (lukas, a dormant l

## Commits

```
dce017d62b artpipe idle_fill: a user timer feeds the art queue when it runs dry (ARTPIPE_IDLE_FILL_EMPTY_ALL_NIGHT)
7efbfd3db7 account_failover review r4: a marker is pending until `use` finishes, and a pass that died before then (stale pending, FROM live) is dropped instead of idling stage 2 for good; stage2.json and the marker written atomically; a failed disarm exits nonzero; switch log says live_after and marker fate; dry-run records carry dry=true; post-DARK and deadline reasons tell the truth; red-first. Lesson filed for the unprobed first real use and the 600 s mid-switch kill
072abc4c33 testq ingest: review r7 - git option parsing skips -c K=V and resolves --git-dir against -C
a58d7b739a testq ingest: review r6 - lock holder scan also matches --git-dir/--work-tree/-C/GIT_DIR aimed at this clone
30536adc39 ledger: file SLOT_BURNACCOUNT_FIX_DORMANT_TIE (account_failover review r3)
84ba14c87a account_failover review r3: stage 2 bounded by lukas's 16:00 reset (TO_RESET), not the meter's next one: no 168 h BURN on the new week, no DARK from a pre-refill reading, --hours always given and timed after the slow status call; vacuous past-deadline test given a target; red-first
24b46ac0f4 ticket RIMMANDRAKE_EXCISE_WORK_HISTORY: 05:04 attempt stalled; owner by card: cut over tonight
5b027fe016 slot_allocator review r2: resumed-transcript idle gaps are not running time; overage credit is chronological; payback credit needs payback time at both interval ends; red-first
ab2ce9f697 ledger: mutation run 20261028T013440 partial collect notes; dispatcher re-run 20261028T095621 launched
44c136d35b mutation: dispatcher target also runs selftest_dispatcher_mut2.py
f67097d77f slot_allocator review: overage accounting or a bad override count can no longer crash decide (owner's N still published); overage_t never steps back; set refuses negative n / non-finite or negative hours; red-first
3ae634035c code review: agents_timeline.py + selftest marked clean (r1 empty after tail-read change)
8baeb3db9d ledger: ops_watch alarm(s) note:ops_watch
8faf9e728b ledger: RUNNER ingest of 1 testq job(s)
d7bf479a17 testq ingest: review r5 - rebase guard also with publication off; re-salt colliding finding names
314901d40e account_failover review r2: failed use drops the marker (stage 2 idled on the wrong account forever); spent lukas goes straight to DARK; malformed reset stamp no longer blocks off; status parse tolerates text around the JSON; failed account_usage not trusted; red-first
9c5bacc96a lesson + ledger: timer mass stop 05:04 traced to a laptop-seat cutover with no resume (TIMERS_DIAGNOSE_SILENT_MASS_STOP note)
099b5faa1e slot_allocator: charge overage from measured helper-hours (span edges over the elapsed interval), not one snapshot; red-first selftests (SLOT_OVERAGE_REMEASURE_BY_HELPER_MINUTES)
52c2f534b4 testq steward: TICK_STOPPED when testq-tick.timer is inactive (was misread as IDLE_EMPTY 'the fill failed?'), red-first
1a7ec4c0ac account_failover review: stage 2 could never fire (status parsed from a 2000-char tail lost its brace); off is DARK not --n 0 (FOUNDRY kept burning); hung meter is a logged skip; no re-switch when lukas already live; red-first
... 15 more: git log --oneline 075e1b66d4..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: for     HOSE_TICK live loop

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
M conversations/2026-10-28-0124-074a4338.md   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M infrastructure/state/code_review/BENCH.jsonl   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M infrastructure/state/ledger/events/BENCH.jsonl   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll.srchash   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNetKernel.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/RM_LevelSolve.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/SelfTest/DirtyReview1022Checks.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/SelfTest/LevelExactChecks.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/SelfTest/NetComponentChecks.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/Source/SelfTest/PitAccessChecks.cs   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/northstar/level_water.py   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
 M src/RimMandrake/FlowWorks/northstar/selftest_level_water.py   helpers mid-flight (FlowWorks hose/surfacegap/flowpins; ledger/code_review shards; conversation record)
```

