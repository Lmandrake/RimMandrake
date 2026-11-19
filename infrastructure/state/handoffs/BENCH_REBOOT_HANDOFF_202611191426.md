# BENCH_REBOOT_HANDOFF_202611191426 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611191117`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
STANDING RULE (owner, 2026-11-19 ~6:05 AM PST): "Ok: standing rule. You offered to run GSS on a broken pipeline. We're not running mods forward until the pipeline is fixed, ok? So now you don't have to ask me anymore for that." No mod is switched on, released or launched until its readiness list reads READY (`standing_rulings.md` §No mod runs forward on a broken pipeline; GimmeSomeSlack's list: `/mnt/d/ClaudeWork/rimmandrake/conductor/pipeline_ready_for_gimmesomeslack_20261119.md`, NOT READY at wrap). Never ask him whether to run a mod. He is at the keyboard in a sitting ("Paper, then biomes", card 5:35 AM PST): paper items left are the phone-alert route card (after checking Pushover facts on its site), which mod Fable builds from the start, the Operations role options; then the biome questions by theme. He wants DETACHED workers, not helpers attached to the window ("You should be using more detached workers. I'm nervous of this many subagents attached to this window"): launch with `detached_helper.py launch --seat CONDUCTOR --item <ID> --brief-file <F> --model <m>`, in a background Bash call (a launch takes 1-2 min), after the item is published; a by-card item's brief must paste `card_capture.py show <ID>`. Briefs of this sitting: `/mnt/d/ClaudeWork/rimmandrake/conductor/briefs_20261119/`. Cards to him: Simplified Technical English; a card he asked for carries `[owner-asked]` in the question text or the delegated-cards hook blocks it. Quote the QUESTION with any short answer of his before building on it (the "Correct, not size" misreading cost a revert today).

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Account runway (FLEET_NOW, read 6:11 AM PST):** the `system` account (this window and its runs) is forecast to run out about Fri 2026-11-20 11:26 PM PST, five days before its reset; left: lukas 100%, steven 55%, system 60%, codex 54%; JPL GenAI UNMEASURED. This morning's repair runs are part of the burn.
- **Codex test of the reviewer instructions FAILED its pass mark** (31 of 35 labels matched, but 2 of the 3 agreed real problems caught; the miss traces to the page's wording). Codex reviews of pipeline code stay off; nothing more runs without his word. Answer file: `D:\ClaudeWork\rimmandrake\conductor\code_review_calibration_answer_page_rule.md`.
- **Three visit improvements await his word** (not blockers): the walk finds no clean site on modded maps; an 18-minute full-list load for one check; the proof spends 37% of its time reading settings.
- **Delegated calls he can veto:** the driver finishes the remaining checks after a FAIL instead of ending the visit; `.service`-suffix launch names listed as "not handled"; alarm log line left to 14 rules; a goodbye now also fires on a message ending "Good night."
- **Phone alerts:** Todoist is retired as an alert route by his word; until a new route is built nothing alerts his phone. He asked whether Pushover runs on Archmagi and on OS X: answered from memory [guess ~85%]; the check on Pushover's own site is owed before his card (`RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED`).
- **Retirement of the old eras is NOT complete** (21 remains, 5 dead, none ticketed before today): reports `D:\ClaudeWork\rimmandrake\conductor\retired_era_remains_20261119.md` and `retired_era_remains_stevedesktop_20261119.md`; SteveDesktop holds eleven stale clones (~168 GB) and its clean-up waits for the soak's end, Fri 5:30 PM PST.
- Code written today had no outside review (his stop); four art-eval files and several pipeline files read DIRTY in `code_review_status`.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_CENSUS_STEVEDESKTOP_ERA_REMAINS_WHILE_SOAK_RUNS` — inventory done (abb7b154e9), nothing changed on the machine, waits to 2026-11-21; NEXT: after the soak's 72 h read (Fri 2026-11-20 5:30 PM PST) launch a detached run that applies the 14 steps in /mnt/d/ClaudeWork/rimmandrake/conductor/retired_era_remains_stevedesktop_20261119.md, archiving uncommitted edits first (owed `RIMMANDRAKE_APPLY_STEVEDESKTOP_CLEANUP_AFTER_SOAK_ENDS_FRIDAY`)
- `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` — detached run live at wrap (brief briefs_20261119/era_finish.md); NEXT: read its result when the run-end wake arrives, tell him what was fixed and which rename tickets it filed (owed `RIMMANDRAKE_READ_ERA_FINISH_RESULT_TELL_HIM_RENAMES`)
- `RIMMANDRAKE_HOLD_UNREADABLE_STORE_TICK_CRASH_BACK_SLICE_TWO` — not touched or read by this window today; NEXT: run `rimflow show` on it and close or carry it with evidence (owed `RIMMANDRAKE_SETTLE_UNREADABLE_STORE_HOLD_NOT_READ_TODAY`)
- `RIMMANDRAKE_PROVE_PIPELINE_CONTROL_ASKS_MET_HE_ASKED_BEFORE` — detached run live at wrap; its report will be /mnt/d/ClaudeWork/rimmandrake/conductor/pipeline_control_complete_20261119.md; NEXT: read the result, open the report in Typora for him and answer his question "Were ALL the tickets related to making our pipeline instantly commandable... worked already?", then launch detached fixes for every NOT MET row (owed `RIMMANDRAKE_ANSWER_HIM_CONTROL_ASKS_MET_OR_NOT`)
- `RIMMANDRAKE_RETIRE_TODOIST_AS_ALERT_ROUTE_IT_NEVER_RANG` — detached run live at wrap (stop posting, close our own tasks in the shared Inbox, record the ruling); NEXT: read its result and tell him open-before, closed, open-after and anything left as origin unsure (owed `RIMMANDRAKE_TELL_HIM_TODOIST_TASKS_CLOSED_COUNT`)
- `RIMMANDRAKE_DROP_RETIRED_SLACK_CHECK_STILL_OWED_AT_EXIT` — detached run live at wrap, closing five GimmeSomeSlack blockers (brief briefs_20261119/gss_last_blockers.md); NEXT: read its result and the report's new first-line verdict; if READY tell him and let HIM say whether GimmeSomeSlack runs; if NOT READY launch detached fixes for the remaining BLOCKS rows (owed `RIMMANDRAKE_READ_SLACK_BLOCKERS_VERDICT_HE_DECIDES_RUN`)
- `RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED` — owed; NEXT: check Pushover's desktop client, platforms and prices on pushover.net, then card him the alert route and backup (Twilio call or none; Todoist struck), with [owner-asked]
- `RIMMANDRAKE_FIX_CALIBRATION_DOOR_SELFTEST_RED_ON_UNTOUCHED_MAIN` — filed; the blockers run was told to fix it if small; NEXT: check that run's result for it, else launch a detached sonnet fix (owed `RIMMANDRAKE_CHECK_CALIBRATION_DOOR_FIX_IN_BLOCKERS_RUN`)
- `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS` — he ruled ("Page says 'not handled'"), so this is unblocked; NEXT: launch one detached Opus run per three files to read the flagged could-not-look places, never one run for all 299

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- `rimflow note` needs `--text`; a bare positional text is refused and the error is easy to miss under `tail` (see: skills/using-rimflow)
- `--owner-said` refuses a quote that is a question; quote only his instruction sentence (see: skills/using-rimflow)
- An item name over 9 words is refused at `file`, and the refusal line is hidden by a narrow grep: check `show <ID>` before briefing a helper with the id (see: skills/using-rimflow)
- `detached_helper.py launch` takes 1-2 minutes and overruns a 120 s foreground Bash: run it in the background (filed: infrastructure/state/lessons/20261119T142726Z-BENCH-detached-helper-py-launch-takes-1.md)
- A short owner answer read without its question became a false ruling for two days (filed: infrastructure/state/lessons/20261119T135415Z-BENCH-owner-answer-read-without-question.md)

## Closed since the last handoff (13)

- `RIMMANDRAKE_FORECAST_ON_SHARED_PLANNER_DROPIN_MIRROR_DEADMAN` — c7e2273f53
- `RIMMANDRAKE_CENSUS_RETIRED_ERA_REMAINS_AFTER_GATE_READS_GREEN` — 00e67455a8
- `RIMMANDRAKE_INSTALL_PERMIT_DROPIN_LIVE_AFTER_CONTROL_FIXES_LAND` — c7e2273f53
- `RIMMANDRAKE_OPEN_ERA_CENSUS_REPORT_FOR_HIM_WHEN_LANDED` — 219ab84f9e
- `RIMMANDRAKE_WRITE_LAWS_FOR_EIGHT_FUZZ_FAMILIES_STILL_UNNAMED` — 75b3856b244c622c6765563bc7ee0e4457c8cfa6
- `RIMMANDRAKE_ENACT_NO_MOD_RUNS_ON_BROKEN_PIPELINE_RULING` — 2cee05e364c1
- `RIMMANDRAKE_TRACE_SLACK_STAGE_SIX_SPEND_BEFORE_FIRST_VISIT` — 8af7715c2c73
- `RIMMANDRAKE_CALIBRATE_ART_JUDGE_BRIEF_AFTER_SIZE_RULE_RESTORED` — 32672dbb0e85
- `RIMMANDRAKE_ADAPT_SUITE_SCENES_TO_EMPTY_GAME_FLOWWORKS_ONLY` — d78464b22365
- `RIMMANDRAKE_ADD_ARCHMAGI_LOAD_MEMORY_TO_FLEET_NOW_SMALL` — e1b3f27729
- `RIMMANDRAKE_MEND_BOUNDARY_ACCEPT_FIXTURE_NOW_NEEDS_MAIN` — 957ec0da0c65
- `RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE` — 9293667cfa
- `RIMMANDRAKE_HARDEN_PUBLISH_PARK_RESTORE_RACE_CODEX_FOUND` — done by verify, no close

## Filed and still open (11) — the next seat's queue

- `RIMMANDRAKE_DECIDE_HOLD_FILE_MIRRORS_STORE_HIS_CALL` — Slice 4 of the pipeline control surface proposed mod_owner_hold.json as a mirror the control store writes; that changes who writes his hold file, so i
- `RIMMANDRAKE_FINISH_RETIRED_ERA_REMAINS_TWENTY_ONE_NO_TICKETS` — Finish the retirement of the pre-Maturation eras: fix the instruction lines that name deleted things, remove the dead, mark the wisdom as history, ext (owed `RIMMANDRAKE_READ_ERA_FINISH_RESULT_TELL_HIM_RENAMES`)
- `RIMMANDRAKE_UNMEASURE_SAND_SHOVEL_ROW_PASSING_ON_EMPTY_MAP` — Pyrelands sand_shovel chain: row sand_carries_the_dig_yield reads def XML on disk, so it passes on an empty game and the certificate refuses its two i
- `RIMMANDRAKE_CENSUS_STEVEDESKTOP_ERA_REMAINS_WHILE_SOAK_RUNS` — Census SteveDesktop for retired-era remains and stale checkouts (read-only while the soak runs); apply the clean-up after the soak ends Friday 5:30 PM (owed `RIMMANDRAKE_APPLY_STEVEDESKTOP_CLEANUP_AFTER_SOAK_ENDS_FRIDAY`)
- `RIMMANDRAKE_PROVE_PIPELINE_CONTROL_ASKS_MET_HE_ASKED_BEFORE` — Prove whether every owner ask for an instantly commandable, low-token pipeline is met: asks, tickets, behaviour run on a throwaway store; ticket what  (owed `RIMMANDRAKE_ANSWER_HIM_CONTROL_ASKS_MET_OR_NOT`)
- `RIMMANDRAKE_RETIRE_TODOIST_AS_ALERT_ROUTE_IT_NEVER_RANG` — Todoist is retired as an alert route: switch the three senders' Todoist posting off, close our own open alarm tasks in the shared Inbox, record the ru (owed `RIMMANDRAKE_TELL_HIM_TODOIST_TASKS_CLOSED_COUNT`)
- `RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED` — Check Pushover's desktop client, platforms and prices on its own site, then card him: alert route and backup (Twilio call or none), Todoist struck
- `RIMMANDRAKE_FIX_CALIBRATION_DOOR_SELFTEST_RED_ON_UNTOUCHED_MAIN` — selftest calibration_registry_door_accept fails 1 of 3 on untouched origin/main (seen by the publish-lane run 2026-11-19, log D:\ClaudeWork\rimmandrak (owed `RIMMANDRAKE_CHECK_CALIBRATION_DOOR_FIX_IN_BLOCKERS_RUN`)
- `RIMMANDRAKE_DROP_RETIRED_SLACK_CHECK_STILL_OWED_AT_EXIT` — GSS test table still owes a retired stage-6 check (P_B4_downed_wire_bursts); visit 2 exit cannot be met (owed `RIMMANDRAKE_READ_SLACK_BLOCKERS_VERDICT_HE_DECIDES_RUN`)
- `RIMMANDRAKE_HOLD_UNREADABLE_STORE_TICK_CRASH_BACK_SLICE_TWO` — The dispatch tick crashes on an unreadable control store again since slice 2 (c180799371): gather's build_facts reads the counts before the hold. Acce (owed `RIMMANDRAKE_SETTLE_UNREADABLE_STORE_HOLD_NOT_READ_TODAY`)
- `RIMMANDRAKE_WIRE_HEALTH_VERDICT_READER_NOBODY_OBEYS_IT` — Wire a reader of Operations' health verdict: its only reader was the retired build tick

## Commits

```
b435d10683 conversations: catch-up 1 record(s)
4844a03c0d GimmeSomeSlack test table: drop retired P_B4_downed_wire_bursts (entry retired by a8d27a3f6b; support only, no bar loosens)
8eb4a961f0 maturation_dispatch: an unreadable control store is a fact of each mod in gather, so the tick holds all instead of crashing (back since slice 2, c180799371)
ed3b6ca7a5 Retired-era lines that sent agents to deleted things rewritten to today's pipeline; BUILD/CHECK/DECIDE seat files and ./bridge foundry removed
fdd7d39037 ledger: RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE clone bundled
236010ee6a maturation: spend rows of ended runs (Dispatch step)
34de2361a2 conversations: catch-up 1 record(s)
fe2ec29407 ledger: detached run on RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE ended
02825fd537 Record: Todoist is for to-do lists only, never an alert route (owner, 2026-11-19); strike stale phone-route lines
de2834357f ledger: close RIMMANDRAKE_PROVE_PIPELINE_READY_BEFORE_SLACK_CEILING_RELEASE (second pass: NOT READY, four blockers)
957ec0da0c boundary_check_accept: its fixture writes a main() that runs its tests (red since 60274d0df2 made main() required)
372f1c5a69 ledger: RUNNER ingest of 0 testq job(s)
9293667cfa ledger: file RIMMANDRAKE_DROP_RETIRED_SLACK_CHECK_STILL_OWED_AT_EXIT (GSS test table owes a retired stage-6 check)
ca131ab038 Todoist alarm posts off by default in phone_push, deadman_check and heartbeat.ps1 (owner by card 2026-11-19)
b0f413796d ledger: RIMMANDRAKE_ADD_ARCHMAGI_LOAD_MEMORY_TO_FLEET_NOW_SMALL clone bundled
0ae60f79fd conversations: catch-up 1 record(s)
d97264b950 ledger: detached run on RIMMANDRAKE_ADD_ARCHMAGI_LOAD_MEMORY_TO_FLEET_NOW_SMALL ended
4d87c693ad ledger: RIMMANDRAKE_ADD_ARCHMAGI_LOAD_MEMORY_TO_FLEET_NOW_SMALL closed (Augur cdf2499)
e1b3f27729 lesson: where FLEET_NOW's generator lives and how to check its SVG
bd69edd20e seat_dirt: land 1 safe path(s) left in the seat clone (conversation records, filed item prose, settled concept folders)
... 64 more: git log --oneline 5011edb756..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-19T14:19:28Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
 M infrastructure/state/ledger/events/BENCH.jsonl   this window (Conductor): ledger lines of this sitting, committed with this handoff
?? infrastructure/state/items/RIMMANDRAKE_RETIRE_TODOIST_AS_ALERT_ROUTE_IT_NEVER_RANG.md   this window (Conductor): the card-stamped item prose, committed with this handoff
```

