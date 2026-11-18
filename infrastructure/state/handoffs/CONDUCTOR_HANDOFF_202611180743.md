# CONDUCTOR_HANDOFF_202611180743 — READ FIRST on wake

Follows `CONDUCTOR_HANDOFF_202611180417`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
🔴 **A SUBAGENT THAT HITS ITS 250-TURN LIMIT LEAVES ITS WORK UNCOMMITTED, AND ITS FINAL MESSAGE TELLS YOU ONLY
WHAT IT WAS ABOUT TO DO NEXT.** Both long agents tonight stopped that way. The judge drain's notification said
only *"Now the two owner re-blocks"*; its clone actually held 24 drained items and a `FAIL 19` acceptance reading,
all dirty. The RC.submit agent's said *"Now wire isolate into the other modes"*; its clone held 360 insertions and
a real oracle. **Both would have been lost to a routine clone cleanup.** (filed: lessons)

**The method that saved them, in order:** (1) measure the CLONE, not the message — run its acceptance test and
`git status --porcelain` there; (2) resume it with `SendMessage` to the task id, whose first instruction is
**"COMMIT what you have FIRST, then every few items"**; (3) only then let it continue. The drain went on to
`PASS 0` in four commits; RC.submit finished in two. (filed: lessons)

🔑 **And the part that is on me: this was already filed on 2026-11-13** — *"In-window helpers stop at a 250-turn
limit mid-task with a one-line partial result… Brief long jobs to land units as they go, and expect to send one
'finish, land, report' message"* (`lessons/20261113T013735Z-BENCH-window-helpers-stop-at-250-turn.md`). I briefed
neither long agent to commit incrementally and rediscovered the trap twice in one night. **Put "commit each unit
as you finish it" in the brief of every agent you expect to run long**, not in the rescue message afterwards.
(filed: lessons) (filed: lessons)

🔴 **And do NOT verify a live agent's work inside its own clone.** To watch RC.submit's new test fail on base I
stashed `maturation.py` there and tidied up with `git checkout -- selftest_maturation.py` — which reverted 283 of
its own uncommitted insertions. I recovered them only because I had copied the file to `/tmp` first, and I re-ran
the suite to prove the restore. Do the red-on-base check in a throwaway `git clone --shared` of the branch; if you
must do it in place, copy every file you will touch first, verify `git diff --stat` after, and tell the agent what
you did when you resume it. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
1. 🔴 **ALL SEVEN tickets you offered a remote builder are landed, closed and their clones deleted**, plus the
   43-item judge drain. Shas: publish untracked-copy `84ca416f3a` · Graffiti kernel6 fuzz `07554749538e` ·
   EK frame judge `9a437178d847` · both judge-card tickets `dbd5c89339be` · wrapup live-clone `cf4a8a4d02f2` ·
   scope_source forgery `895f0834c356` · re-pin anchor `e881b97715cb` · worker map gate `ab3cb4372d68` ·
   RC.submit `13db68e8ed3b` · drain `627dc5790d6a`. Every acceptance reading in this wave was re-measured by me,
   not taken from a builder's report.
2. 🔴 **An instrument has been reporting GREEN over three checks that have never run.**
   `contracts/replay.py:40` pins `BASE = "c8d1d12855"`, which `git cat-file` calls *"Not a valid object name"* —
   in a fresh clone AND in this repo. So replay families C2, C4 and C8 cannot start, and the runner still prints
   `RESULT: GREEN`. **Two independent agents hit it tonight** by different routes (the drain via
   `CONTRACTS_EXCISE_ARBITER_REPLAY_FAMILIES`, the worker builder via `selftest_contracts`), which is why I trust
   it is real and not a clone artifact. Filed `RIMMANDRAKE_REVIVE_REPLAY_BASE_SHA_GREEN_HID_THREE_UNRUN`.
3. **The pipeline door is red on `origin/main` on this machine and it UNDOES your commit.** Four door tests fail
   there for reasons unrelated to any change: `selftest_dispatch_two_games` (6 FAIL here, **5 FAIL in a Linux
   container too**), `selftest_maturation_dispatch` (CRASH), `selftest_designer_stage` (1 FAIL on a hard-wired
   seat-clone path), and `selftest_seat_restart(+_death)` until I fixed those two. I landed four commits with
   `RM_PUBLISH_SKIP_PIPELINE_CHECKS` naming pinned evidence, each after proving innocence by stashing my own paths
   and re-running. **The two_games failures look like your own 2026-11-16 "no waiting for game" promise not
   actually holding** — I filed it rather than touching the test, because deciding whether the test or the
   two-game dispatch is wrong is a design call: `RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH`.
4. **I landed a calibration that makes advance refusals BIND, and you can veto it.** `judge_calibration.json`
   gained a `maturation_advance` row in `13db68e8ed3b`. Without it `status()` reads UNTESTED and every advance
   refusal stays advisory for ever; with it, `REFUSAL_NOTHING_COULD_EVER_PASS` can rise from ordinary pipeline
   work and tell the Conductor (it blocks nothing: `may_judge()` has no production reader, measured 2026-11-18; see RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED). I verified CALIBRATED was EARNED (a real `RC.run_check` over 3
   planted cases, 2 refuse + 1 pass, all as planted), not declared. Two consequences are filed, not silenced:
   the suite already reaches **0.75 refused against the 0.70 family limit**, so it can ring on its own fixtures
   (`RIMMANDRAKE_WIDEN_FAMILY_TRIP_MARGIN_SUITE_ALMOST_RANG`); and the release `clear()` has no CLI verb and no
   caller in `src/` — I probed it and it works called directly, so it is a missing door, not a stuck alarm
   (`RIMMANDRAKE_EXPOSE_REFUSAL_RELEASE_VERB_CLEAR_UNREACHABLE`).
5. **Two drained items are left blocked ON PURPOSE, waiting on your ruling — no proof can close them.**
   `SEKKULAATH_RISING_DESIGN_CRATER_EVENT` (the crater event's two design clauses from your 2026-10-10 card 19)
   and `ASSAILANT_WARLAB_BUILD_MERGE` (hard reads 1 and 3 of the warlab gate-order brief; read 2 you already ruled
   2026-11-03). The drain's 91 ledger events are all seat OWNER with `ranBy=AGENT` and
   `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, so `is_his_act` reads **False** and your interaction
   clock is untouched; 66 carry a stamped seat-boundary override, which is the documented loud path.
6. **Carried from the last handoff and still true: recalibration is owed before the judge's refusals mean
   anything.** `bar_rule.py` and `coverage_judge.py` are in `refusal_contract.brief_hash`, so the coverage judge's
   brief is UNTESTED until `RIMMANDRAKE_RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE` runs. Your 2026-11-17
   card's four rules bind once the judge prompt is edited and recalibrated — that has not happened.
7. **`OPS_WRAPUP_SKIP_CLONES_OF_LIVE_FLEET_RUN` landed NARROWER than its own sentence** (per-mod phase gap, not
   fleet-wide): measured, the literal bar would have suppressed the Greentide **true** positive and blinded
   `wrapup.debris_standing` for ~8 h across 23 mods. Your call if you disagree; the reason is on the item.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `NOTHING_IS_IN_FLIGHT` — no subagent is running, no clone is left, the tree is clean and everything is pushed;
  the ten filed findings below are unclaimed work, not half-done work. NEXT: pick one of them, or ask him which.
- `RIMMANDRAKE_REVIVE_REPLAY_BASE_SHA_GREEN_HID_THREE_UNRUN` — filed with four criteria; a GREEN covers three
  checks that cannot start. NEXT: make an unresolvable `--base` exit non-zero FIRST (criterion A1), then choose a
  live base and re-run C2/C4/C8, recording whatever they really say.
- `RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH` — filed; red on main here AND on Linux. NEXT:
  settle whether the test or the two-game dispatch code is wrong — do NOT relax the test — quoting the evidence,
  and treat his 2026-11-16 "no waiting for game" as the bar.
- `RIMMANDRAKE_SPLIT_RED_FROM_UNMEASURED_STATUS_ENTRY_LIES` — filed; `modcheck.verdict_for` records `RED` for a
  real FAIL, for a suite that measured NOTHING, and for a gate that SKIPPED a chain. NEXT: build it, honouring
  criterion A4 — no input that reads non-GREEN today may read GREEN after.
- `RIMMANDRAKE_SPLIT_UNREADABLE_LEDGER_FROM_FORGED_SOURCE_CITATION` — filed; `source_errors` guards with
  `owner_ev is not None` but production passes `{}` for an unreadable ledger, so a real OWNER citation reads as a
  forgery. NEXT: copy the pattern from the landed `inventory_errors` fix (895f0834c356) — key on falsiness.
- `RIMMANDRAKE_WIDEN_FAMILY_TRIP_MARGIN_SUITE_ALMOST_RANG` — filed with three options and a recommendation.
  NEXT: choose option 1 (suite verdicts never count toward a family window) unless he prefers otherwise; do not
  tune the threshold.
- `RIMMANDRAKE_EXPOSE_REFUSAL_RELEASE_VERB_CLEAR_UNREACHABLE` — filed; `clear()` works but has no door. NEXT: add
  a `release` verb taking a subject and a required `why`, keeping the trip count and history.
- `RIMMANDRAKE_SHORTEN_BRAKE_PASS_STEWARD_MISSED_ITS_BEAT` — filed; `brake_release.decide` runs one `fill_plan`
  per mod and uses one, eating steward's 300 s heartbeat budget. NEXT: make the pass cost bounded, and keep
  "planned and not braked" distinct from "not planned this pass".
- `RIMMANDRAKE_REORDER_COVERAGE_BEFORE_EXAM_SIX_RETAKES_PAID` — filed; the successor nobody had filed, and its
  authorising decision is a DELEGATED evidence-for-ask yes, not his word. NEXT: read
  `maturation_autonomy.exam_gate` first and decide whether the judge's reading leans on an exam-passed tree — if
  it does, the reorder needs him, not a builder.
- `RIMMANDRAKE_NAME_SOAK_SILENT_EXIT_INTERRUPTED_LOOKS_IDLE` and
  `RIMMANDRAKE_ROUTE_SOAK_READ_VIA_TAILNET_DESKTOP_SEES_NOTHING` — both filed. NEXT: take the route one first; a
  soak the Desktop cannot read is why the previous handoff reported a running soak as dead.
- `RIMMANDRAKE_SPLIT_ONLY_NAMES_LONG_LIST_CRASHES`, `RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED`,
  `RIMMANDRAKE_LIST_WALK_SUITE_IN_HARNESS_MUTANTS_SURVIVED`'s sibling `EK_FAULT_HARNESS_SCOPE` — small and
  self-contained, each with a reproduction. NEXT: take any as filler work.
- `TWO_PARKED_TO_THE_RESET` — `RIMMANDRAKE_EXPLORE_OPERATIONS_OPTIONS_AFTER_WEDNESDAY_RESET` (his words: *"Bring
  it back up then and we'll explore the options together"*) and `RIMMANDRAKE_REASK_FABLE_FROM_START_WHEN_MOD_IS_FREE`.
  Wednesday is the token reset day, not a deadline. NEXT: raise both with him after the 2026-11-18 reset — his
  call to open, not yours.
- `EVIDENCE_QUALITY_SPEC_0.3.0` — carried two handoffs now, untouched: reviewed twice, nothing built, Part B
  withdrawn, Part A blocked because it changes POLICY (extra automatic attempts past the one-per-visit rule he
  bounded 2026-11-14). NEXT: put Part A's policy question to him before any code, then build change two first.
- `LIVE_HALVES_UNRUN` — two landed fixes have an unexercised live half, both recorded UNRUN in their closes, not
  hidden: the worker's map gate needs one lane job on a kept game, and the soak-route fix needs one real read from
  this Desktop. NEXT: run the worker one when the bench is free (it is hours into a 72 h soak that must not be
  disturbed).

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A turn-limited agent's clone holds uncommitted work its final message never mentions; measure the clone, then resume it with "commit first" (filed: `lessons/20261118T055208Z-UNSEATED-subagent-that-hits-its-250-turn.md`).
- Verifying a live agent's work in its own clone destroyed 283 of its insertions; use a throwaway clone (filed: `lessons/20261118T070837Z-UNSEATED-verifying-running-agent-s-work-its.md`).
- A pinned literal sha rots and takes a GREEN with it: `replay.py`'s `BASE` names no object, so three families never ran (filed: `lessons/20261118T055208Z-UNSEATED-pinned-literal-sha-code-rots-silently.md`).
- A calibration status, not the wiring, decides whether a gate's refusal binds: an UNTESTED family stores refusals for ever (filed: `lessons/20261118T074301Z-UNSEATED-ticket-can-need-third-file-nobody.md`).
- `owner_ev is not None` is not "we have a reading": `CT.owner_events` returns `{}` for an unreadable shard, so a real event reads as forged (filed: `lessons/20261118T045320Z-UNSEATED-guard-written-as-owner-ev-not.md`).
- A pipe eats the exit code you are about to report; it told me a FAILING acceptance test had passed (filed: `lessons/20261118T032319Z-UNSEATED-pipe-eats-exit-code-you-are.md`).
- The pipeline door is red on main here and undoes your commit; prove innocence by stashing your own paths (filed: `lessons/20261118T041633Z-UNSEATED-pipeline-door-red-origin-main-this.md`).
- A Linux-only reading must say UNMEASURED, not FAIL: `/proc` and `pidfd` absences were recorded as verdicts about the code (filed: `lessons/20261118T041633Z-UNSEATED-linux-only-reading-must-say-unmeasured.md`).
- A handoff pointer's claim about the ledger is a claim; two were wrong (filed: `lessons/20261118T032326Z-UNSEATED-handoff-pointer-s-claim-about-ledger.md`).
- The Desktop cannot ssh to SteveDesktop at all, so every Steve reading here is UNREACHABLE while the machine is up (filed: `lessons/20261118T033258Z-UNSEATED-desktop-cannot-ssh-stevedesktop-at-all.md`).
- A mutation harness's "survived every offline suite" is a claim about its 13-entry hand list, not the repo's 29 suites (filed: `lessons/20261118T032335Z-UNSEATED-mutation-harness-s-survived-every-offline.md`).
- A ticket's quoted base reading decays; re-measure at the commit you branch from (filed: `lessons/20261118T032335Z-UNSEATED-ticket-s-quoted-base-reading-decays.md`).
- A ticket's literal sentence can be the wrong bar; land narrower and say so on the item (filed: `lessons/20261118T041641Z-UNSEATED-ticket-s-literal-sentence-can-be.md`).
- The 46,000 NVMe events were one repeated message on a drive no longer in the machine; verify by serial (filed: `lessons/20261118T033537Z-UNSEATED-46-000-nvme-bad-block-events.md`).
- `git reset --keep` refuses on an identical untracked file but silently overwrites an ignored one (filed: `lessons/20261118T032341Z-UNSEATED-git-reset-keep-refuses-any-untracked.md`).
- `modcheck.verdict_for` collapses "measured nothing", "gate skipped" and a real FAIL into one RED (filed: `lessons/20261118T032924Z-UNSEATED-rimmandrake-silent-failure-audit-s-first.md`).
- `rimflow` refuses every verb without a seat: `RIMFLOW_SEAT=CONDUCTOR` is needed on each call in this window, `./game` included (see: the refusal names the three ways to set it).
- `./publish` cannot re-add a path it is deleting: a close that moves item prose needs `git commit` by hand, then a bare `./publish` (see: the refusal names the pathspec).

## Commits

```
1baf64a3fc lesson: a calibration status, not the wiring, decides whether a gate's refusal binds
6a6b180937 RC.submit closed, and the two risks it surfaced filed rather than tuned away
13db68e8ed maturation: advance submits its verdict, so a stage refused again and again rings
cd0a454ea1 seat_dirt: land 2 safe path(s) left in the seat clone (conversation records, filed item prose)
455a3ce903 ledger: DISPATCHER notes (1)
1fe07bf0f1 ledger: live sweep OPS_WORKER_CLONE_POOL_RESTORE_HMOQ kept
ad561fd3d9 ledger: DISPATCHER notes (1)
1f3f9c1940 lesson: checking a live agent's work in its own clone nearly destroyed it
2d391770a6 worker ticket closed, with its 11 red-on-base cases and the live half named UNRUN
ab3cb4372d worker: stop a kept game that can never make a map, so the next job cold-starts
cb5aa30dc3 lesson: scratch_clone reads RM_SEAT, not AGENT_SEAT
14e4357160 rimflow: split the cleanse apply ticket into planner, owner-marks check and write; case files watched failing; plan JSON
3eb4de4094 ledger: DISPATCHER notes (1)
bab5b4087c ledger: close FOLD_OWNER_MARKS at baaea8888a; note on CLEANSE_APPLY lane; lesson
baaea8888a design: fold owner marks into Abyss and TheRot cleanse proposals
3d6fb47d43 seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose)
b6645cfc07 ledger: owner allows the two judge gap fields on the counts ticket
4d28714caa ruling: Terminal Biomes keeps one signature for four seas, built in waves biome by biome
89e515fa3b lessons: a turn-limited agent's clone holds uncommitted work; a pinned sha rots with its GREEN
64eb69ce1d seat_dirt: land 2 safe path(s) left in the seat clone (conversation records, filed item prose)
... 16 more: git log --oneline de0bf78908..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Working tree clean.

