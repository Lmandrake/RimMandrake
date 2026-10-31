# FOUNDRY_HANDOFF_202610311937 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610302229`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next session hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
The arena trial is NOT running and the gate cannot yet pass the reference fix: arena_gate.py s_proof -> proof_target -> proof_touches (lines ~1389-1422, 1486-1488) ignores the `run_selftests.py --only <selftest>` target, so 13 of the 26 kept tasks get an `invalid` verdict (runner stops) and 5 more get `fail` with the REFERENCE fix (ARENA_PROOF_FIX_BLIND_ONLY_TARGET). The freeze (pool_sha256 6d0ef9951f22411ebdd31dd0d649945ac176dfccf5d5d6608826f14f74ab2319, 156 tasks) was done before anyone ran the reference fix through the whole real gate. Gate round 3 (builder a1dabe65c454d819a, deadline 3 PM PDT Oct 31) is fixing it and re-sweeping all 26; the rule from the Conductor: relaunch ALL THREE arms together on identical gate code, only if >=20 of 26 tasks PASS at the reference; otherwise do not relaunch, tell the Conductor (stop-the-trial decision for Mandrake). Replay line: 8 AM PDT Sunday Nov 1, estimate 10-14 h. (filed: lessons)

## What the owner should see

<!-- Findings that need the owner's eye or decision: a number nobody ruled on, a change they can veto, anything shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- Mandrake's rulings enacted or pending this wave (all on the ledger): raider fill depth line 4 notches (2 m) with x18 fill and gunners shoot, closed + live-proven (3c4a9ba173); Dubs interop cut, RM_Thirst only, Dubs full + Thirst add-on marked incompatible (4e353bf2e7, docs cleaned 3b976698ce); Haiku banned for RimMandrake, Sonnet 5.5 is the floor (Agent_Policy.md edited a46912fdc9; hook files .claude/hooks/block_agent_without_model.py, block_unbounded_agent.py, selftest_block_agent_without_model.py still accept/mention haiku, not edited).
- The trial list shrank 29 -> 26 tasks (FILLQUEUE, FLYER_MOTION, EVIDENCE_COVERS excluded, trial_exclusions.json, 5e88b802fb); if gate round 3 leaves fewer than 20 passable the Conductor takes a stop-the-trial decision to him. Power at 26 tasks is slightly lower than the power card (simulated at 29).
- Owed to him by queue: Abyss muffle ships ON by default and the Twilight cast blessed with the draft's recommended answers (both on the ledger, NOT yet enacted).

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_OR_TOPIC — state; NEXT: <one imperative action>`. A pointer without a NEXT: measured ~0% pickup; with one, near-100%. -->
- `ARENA_GATE_ROUND3` — builder a1dabe65c454d819a writes /mnt/d/ClaudeWork/rimmandrake/foundry_arena/gatefix/round3/progress.md and launcher.log lines `GATE ROUND3 START` and `GATE ROUND3 PASSCOUNT <n>/26 <sha>`; NEXT: read round3/progress.md, if PASSCOUNT >= 20/26 apply its list of tasks that must leave the list (trial_exclusions.json, rebuild + commit trial_tasks.json via arena_trial.py build) and then relaunch all three arms, else tell the Conductor and stop.
- `ARENA_SPEND_FIX3` — builder af874d3f188c7006b fixing ARENA_SPEND_FIX_DEFAULT_ROOT_DROPS_BUILDER, ARENA_KILLED_TESTER_FIX_VOIDS_WHOLE_TRIAL (ralph_a/trio were stopped mid-run at 12:19, so the gap may be in the real data), ARENA_DQ_TESTER_FIX_VOIDED_ORPHAN_VIOLATES; writes /mnt/d/ClaudeWork/rimmandrake/foundry_arena/spend_fix3/progress.md; NEXT: read its progress file, confirm published + importable, rerun arena_answer_check.py (expect 28 pass, 0 fail, 0 unmeasured).
- `REPLAY_RELAUNCH` — all three units stopped (rm-arena-replay-{v3,ralph_a,trio}; logs saved in /mnt/d/ClaudeWork/rimmandrake/foundry_arena/replay/logs/attempt1 and attempt2); launcher agent ab8c89dbeca2521dd (resumable via SendMessage) knows the steps: confirm HEAD has the gate/spend/anchor commits, clear STOP files in replay/ctl/*, move old logs to a new attemptN folder, `--plan` must print 26 (or fewer after exclusions) tasks in trial_tasks.json order, start the 3 units once via systemd-run --user with the absolute arena.py path (`arena.py trial-runner --arm <arm>`), supervise 6 min, log PROVEN 5MIN to replay/launcher.log; NEXT: after ARENA_GATE_ROUND3 passes the floor, resume the launcher with the go.
- `ARENA_ANCHOR_CLOSEOUT` — rm-arena-anchor.timer publishes ledger anchors every 10 min from /home/mandrake/rm/anchor; at trial end run `python3 src/RimMandrake/Utils/arena/arena_anchor_publish.py --final` (exit 0) and pass `--ledger /home/mandrake/rm/anchor/infrastructure/state/ledger/events.jsonl` to arena_analysis.py and arena_spend.py; NEXT: at close-out, run that before the analysis.
- `ARENA_DAY2_PREFLIGHT_SEVEN` — 7 items filed --for FOUNDRY, not started: ARENA_TRIAL_FIX_STOPS_LIVE_ARMS (do first), ARENA_TRIAL_FIX_V3_LOCKS_READ_RED, ARENA_LANE_FIX_EVENTS_REJECTED_UNSIGNED, ARENA_LIVE_PARK_FIX_NEVER_REACHES_CONDUCTOR, ARENA_LIVE_POOL_BUILD_SWAP_ABSENT, ARENA_TESTPILOT_BUILD_UNIT_NEVER_WRITTEN, ARENA_STEVE_LANE_INSTALL_NOTHING_THERE; NEXT: triage ARENA_TRIAL_FIX_STOPS_LIVE_ARMS in a helper before day 2.
- `ARENA_DAYZERO_PROVE_GAME_DEV_BAR_LIFTS` — mark implemented when arena day 0 closes; that alone lifts the game-dev bar (6347f35343); NEXT: mark it implemented when day 0 closes.
- `CLOSED_LOOP_PROVE_EDIT_RUN_LOOK_AGAIN` — Mandrake: "edits the code, runs the code, looks at the outcome, edits again", blind checker only at the end of the cycle, not inside the loop; NEXT: after arena day 0 closes, staff the items `rimflow pilot` routes with rm-testpilot helpers (one agent per problem, end to end, fix included, one bridge holder at a time, blind checker at the end), and measure closed items per day against the old route.
- `ABYSS_MUFFLE_DEFAULT_ON` and `TWILIGHT_CAST_BLESSED` — Mandrake's rulings, on the ledger, to enact after the relaunch with helpers; NEXT: find the two ledger notes (rimflow show / grep Abyss muffle, Twilight cast) and enact them.
- `QUARRY_SPLIT_TICKETS` — the Conductor's helper is splitting Quarry into separate tickets for FOUNDRY; NEXT: claim them when they appear in `rimflow next`.
- `CODE_REVIEW_OWED_ARENA` — every touched arena file is DIRTY in code_review_status.py (judge, tasks, reader, trial, analysis, spend, eventlog, anchor_publish, gate, replay_run, ralph_a_loop, v3_control, arena_safe_git, helper_capture, and raid_trench_proof + selftest + the FlowWorks thirst/raider files); NEXT: after the trial starts, run a GPT review (consult enrolment for foundry is missing) or a fresh Opus full-file review per file, then mark-clean.
- `AFTER_TRIAL_ITEMS` — ARENA_JUDGE_HONOUR_READER_UNSCORE superseded; owed after the trial: reader items (PASS: 0 FAIL: 2 now fixed; PYTEST_SHORT_FRAMES, CUT_SUMMARY_LIFTS_FILE, SHORT_NAMES_UNSEEN), ARENA_VET_FIX_SANDBOX_FAILS_REWRITTEN_FIVE, ARENA_BANK stratum-B (~14 more rescuable rejects), arena_gate.py import DUMP_ROOT from game_paths, TRIO_CRITIC_WIRE_LIVE_PLAN_TOO, TRIO_SELFTEST_VERIFY_NO_REAL_RIMFLOW, ralph_a/trio --tasks order check, Agent_Policy hook files; NEXT: file/claim these after the trial completes.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives — append it to the lessons file the moment it is learned, then cite `(filed: LESSONS)` or `(see: <doc>)`. Never re-explain a trap that is already recorded. -->
- A gate that is never run against the reference fix end to end proves nothing: freeze only after the reference passes every step on every kept task (filed: ARENA_PROOF_FIX_BLIND_ONLY_TARGET).
- Helper types lacked SendMessage until the Conductor added it for new spawns; running helpers cannot message main, so have them append milestones to a log file and watch it with Monitor (filed: replay/launcher.log protocol).
- `systemd-run` units need ABSOLUTE script paths; a relative arena.py makes the signing entrypoint check see __main__ None (filed: ARENA_REPLAY_* notes in replay/progress.md).
- The arms import arena_analysis.py/arena_spend.py per task: an on-disk edit reaches running arms, keep every state importable (see handoff for the builders). (filed: lessons)
- A Haiku census was partly wrong (6 wrong, ~5 missed) when Sonnet re-checked it; owner banned Haiku for RimMandrake (filed: memory no-haiku-for-rimmandrake).

## Commits

```
9cc8a34100 runbook: measured seat return after reboot, power cut stated unmeasured
b8f0cb67ba census: later_fixes window opens at the fix commit (finds TANK_SETTLE's 1d77c17651); clear 8197e06e6e so the census reproduces the frozen pool
0674fcd016 steve seats: logon task in bootstrap, runbook, and an alarm when they are absent after boot
80085de18a ledger: DISPATCHER notes (2)
04292c4fe5 ledger: ARENA_ANCHOR note (v3:60, @roster:2)
f86a34faf2 lesson: WSL crash NUL tails in seat transcripts voided the arena meter
d54830fb80 ledger: ARENA_METER_FIX_BAD_LINES_VOID_VERDICT implemented at 69b2435365 (+ proof note)
49d67776cc ledger: file ARENA_PROOF_FIX_BLIND_ONLY_TARGET (gate proof step blind to run_selftests --only target)
afc154d725 ledger: DISPATCHER notes (0)
69b2435365 arena_spend: a stale NUL crash tail in the harness's own seat transcripts is reported, not blocking; every near miss stays UNMEASURED (ARENA_METER_FIX_BAD_LINES_VOID_VERDICT)
ee8f6a1f62 ledger: backstop stage 1 note, stage 2 owed, lease released
95e2533c7d ledger: birth-fix item closed at e4711f7ef9, selftest clean, goodbye follow-up filed
b11f4d3a0f ledger: RUNNER ingest of 1 testq job(s)
ee29010378 ledger: replay_watch clean marks
974b2a1073 replay_watch: a fresh attempt reads 0 done; a restart's failure alarm outlives launcher.log; fsync the budget
57cc5281e4 ledger: seat_restart.py clean at ef583b5842
e4711f7ef9 seat backstop: size limit for busy windows (soft 110k tell once, hard 200k at a safe boundary), wake digest, birth fix
6220d650f1 ledger: ARENA_PUBLISH_DQ_FIX_PARKED_REJECT_VIOLATES implemented at 0bac0b966d
2e2fcb2b48 ledger: ARENA_ANCHOR note (v3:52, @roster:2)
145797496e ledger: file ARENA_PUBLISH_DQ_FIX_PARKED_REJECT_VIOLATES
... 561 more: git log --oneline 4008806aa5..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
M deployed/config/ModsConfig.before-tier-gimmesomeslack.xml   [not mine: older generated/other-seat file]
 M src/RimMandrake/Utils/arena/arena_gate.py   [gate builder a1dabe65c454d819a, in flight]
 M src/RimMandrake/Utils/arena/selftest_arena_gate.py   [gate builder a1dabe65c454d819a, in flight]
?? .claude.json   [not mine: older generated/other-seat file]
?? "D:\\ClaudeWork\\rimmandrake\\foundry_arena\\gpt_review.md"   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_20261017T084726.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_20261017T084802.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_20261017T092155.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_20261017T110253.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_p00.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_p03.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_p10.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S1_p14.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_20261017T084824.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_20261017T092355.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_20261017T110404.txt   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_p00.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_p10.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_p30.png   [not mine: older generated/other-seat file]
?? Transient/fw_scenes/live/S2_p60.png   [not mine: older generated/other-seat file]
... 124 more uncommitted paths (by top-level dir: Transient 118, conversations 6): git status --short
```

