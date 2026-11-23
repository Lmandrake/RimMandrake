# Census: rules, roles, hooks and gates that are best retired

Item: `RIMMANDRAKE_CENSUS_RULES_BEST_RETIRED_ANCIENT_STUFF_IN_THERE`. Run 2026-11-23, 8:37 to about 9:45 AM PST. The
run deleted nothing and edited no rule file. Other runs edited rule files during this run. The run re-read
`standing_rulings.md`, `CLAUDE.md` and `dispatcher_schedule.json` at origin/main at about 9:20 AM. Each reading below
was taken in this run and is [measured], unless a row says [guess ~N%] or UNMEASURED.

## 1. Summary

| class | RETIRE | REVIVE |
|---|---|---|
| A. a role, seat or timer that does not run | 7 | 1 |
| B. a rule that waits on something that is gone | 4 | 1 |
| C. a hook or gate whose danger is gone | 2 | 0 |
| D. a rule that a later ruling replaced or restates | 6 | 0 |
| E. a procedure nobody follows | 2 | 3 |
| F. an incident, alarm or owed item that lives off a retired thing | 5 | 0 |
| G. a file that nothing loads or cites | 3 | 0 |
| **total** | **29** | **5** |

Looked at: 22 role files, 49 sections of `CLAUDE.md`, 67 headings of `standing_rulings.md`, 34 hooks, 49 timers, 10 open
incidents. The rest of these is KEEP (Table 4).

Of the 29: 18 rest on no words of his (Table 1, the Conductor decides). 11 rest on his words (Table 2, he decides).

The ten largest RETIRE candidates:
1. **The Producer role** (last run 2026-11-01): 242 lines of instructions, and forecasts that Operations still writes to it.
2. **The Auditor role** (last run 2026-11-01): 321 lines, three programs (728 lines) and four tests.
3. **The health verdict and "the system first" section**: 546 lines of program and 5 tests; no pipeline reads the verdict.
4. **The daily agent-improvement pass**: 1,034 lines of program, run every day; its last edit was for 2026-11-02.
5. **The maturity dashboard, the goal sheet and the hub page**: 1,176 + 291 lines; their data stopped 2026-09-10 and 10-02.
6. **The plan priority list and its alarm**: 256 lines; a 10-day incident that 19 model answers did not close.
7. **The wake-up ring for idle seats**: last ring 2026-11-02; the only seat left has waking switched off.
8. **The nightly full FlowWorks sweep**: about 4 hours of planned SteveDesktop time last night, on a mod still in production.
9. **The old rimflow manual and root leftovers**: 1,299 + about 400 lines that nothing loads.
10. **The Artist role**: 133 lines of instructions and a test; the role has never run.

## 2. Table 1: RETIRE, no words of his (the Conductor decides)

| candidate and where | what it tells an agent or machine to do | evidence that it is dead | what is lost; who still reads it | size |
|---|---|---|---|---|
| **The SteveDesktop processor retest timer** (A), `~/.config/systemd/user/steve-cpu-retest.timer` | run a retest step every 60 seconds | `state.json` reads `END_FAULT`, last event 2026-11-01 8:43 AM. Item `CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH` reads done (2026-11-19). `list-timers` shows it fired 57 s before the read | nothing; the readings stay on D:. `rm-steve-fault.timer` watches the machine and stays | 1 timer, 1 service, 1 script on D: |
| **The wake-up ring and idle bring-back** (A), `dispatcher_schedule.json` blocks `idle_bringback`, `busy_waiting`, `no_handoff`, `focus_cap`, `caps` | ring an idle seat, then restart it | Dispatcher journal: last `ring` 2026-11-02, last `busy_waiting` and `bringback_end` 2026-11-02, last `woke_no_handoff` 2026-11-02; probe: `incident` and `publish` rows from today. `focus_cap.seats` is `[]`. The one seat row, BENCH, has `wake: false` | check first: `doorbell.py` (224 lines) also gives `claude_ancestor` to other hooks, and incidents can use the ring code. `priority.py` reads `focus_cap` | 5 config blocks, part of `dispatcher.py` (2,864 lines), `selftest_idle_bringback.py`; exact lines UNMEASURED |
| **The three switched-off clock units** (A), `src/RimMandrake/Utils/systemd/rm-dispatcher.*`, `rm-ops-watch.*`, `rm-restart-reconcile.*` | start the Dispatcher, ops_watch and the restart check on their own timers | `list-unit-files`: all three timers read disabled. Their work runs elsewhere: `restart_reconcile.json` is from 9:02 AM today, and `rm-metronome` and `rm-metronome-sense` fire | none found. `dispatcher_schedule.json` still names `rm-ops-watch.timer` as the unit. Check that no promise names them | 6 files |
| **The plan priority list and its alarm** (F), `infrastructure/state/priority_list.json`, `priority_list.py`, the `PLAN_DISTRESS` rule, requirements "Plan-aware by one short list" and "Busy is not progress" in `operating_requirements_2026-11-01.md` | the Producer sets a list; the list goes first; an old or spent list alarms | set last 2026-11-14 by the Conductor; all three entries are closed. Incident `plan-20261113082446` is open since 2026-11-13: 57 rows, 19 acks in `told.jsonl`. Operations says each day that no work stops for it | the order now comes from the Maturation Pipeline, the List Pipeline and `CONDUCTOR_GOALS.md` (block 10 is from today). Readers: `priority.py`, `cli.py`, `owed.py`, `follow_through.py`, `ops_watch.py` | 256 lines, 1 test, 1 alarm rule, 1 incident |
| **A dropped item used as a notice board** (F), `V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE` in `operations.md`, `conductor.md`, `producer.md`, `auditor.md` and five role rows | write each role's notes on this item | the OWNER event of 2026-11-01 dropped it ("old-role machinery is over"). Operations wrote to it on 2026-11-21 and 11-23. One symptom is already filed: `RIMMANDRAKE_ROUTE_REPLAN_REQUESTS_TO_CONDUCTOR_PRODUCER_OFF` | a new home for `OPS PROPOSAL` and `OPS DECISION` notes: an open item. `alarm` items name it as parent, so the filers must change too | about 25 lines in 4 role files, the filers' parent field |
| **"Until the shared helper pool gives a reservation, you run no helper"** (B), `operations.md` about line 432, and the same clause in `auditor.md` | run no helper until item `HELPERS_BUILD_SHARED_CAP_ACROSS_ROLES` is built | that item was dropped 2026-11-01. The clause can never end | none: the rule is simply "no helper" | 2 lines each |
| **"A program that does this scan is owed"** (B), `auditor.md` line 201 | wait for `AUDITOR_BUILD_WAITING_INDEX_REQUEUE_SCAN` | dropped 2026-11-01 | goes with the Auditor, Table 2 | 1 line |
| **The rulings reconciler** (B), `conductor.md` lines 74, 106, 289 | read the mismatches that a program finds between rulings and state | no program exists: `git grep -il reconciler` over `src/**/*.py` gives 0 files (probe: `canon_sweep` gives hits). Item `RULINGS_BUILD_STATE_RECONCILER_NEWEST_WINS` is still proposed | nothing. `rm-follow-through` (new today) and the delegated digest cover part of it [guess ~60%] | 3 lines, 1 item |
| **The innovations list step** (F), `conductor.md` line 107 and step (e) line 305 | point his digest at `innovations.md` | the Innovator was retired today (`f1f47631e6`). The file's last change was 2026-11-19, a header stamp | nothing | 3 lines |
| **"The nightly is HELD until a mod passes"** (B), `operations.md` (lessons), `conductor.md` (throughput), `standing_rulings.md` §The nightly checks finished mods only | treat a missing nightly as no fault | `nightly_scope.py show`: 41 tests from 1 finished mod. The nightly ran at 3:00 AM today and reads one red. `timers_held.json` is empty. A reader of the old line can ignore a really missing nightly | keep his card and the scope. Remove only the held clauses | about 12 lines |
| **The unclosed-queue-item warning hook** (C), `.claude/hooks/warn_unclosed_queue_item.py` | warn when a commit removes a heading from a queue file without a `Closes:` line | the queue files are generated and gitignored, so the hook skips them. 0 outputs in 10,808 transcripts of 30 days (probe: the generic-helper refusal shows 171) | nothing. The ledger holds each item | 149 + 166 test lines, 1 settings row |
| **The bench-mode hook and the mode file** (C), `.claude/hooks/bench_mode.py`, `infrastructure/state/MODE` | on "I'm here", print the Charter's Posture section; on "stepping away", say "rejoin the BELT" | last arrival hit 2026-11-05, and that one was in a test helper's transcript. 70 departure hits, last 2026-11-21. There is no belt and no second seat. `MODE` reads `belt`, last set 2026-09-20 by a retired seat | `conductor_goodbye.py` handles his goodbye (35 hits). `cli.py` reads `MODE` only to hold back items that need him | 78 lines, 1 settings row, 1 state file, a few lines in `cli.py` |
| **The build pause of October** (D), `debug_process.md` §1 and the pointer in `CLAUDE.md` §How we debug | stop all content, and lift the pause when every mod has a script | he lifted it on 2026-10-02, quoted in the section. Its umbrella item and metric describe the pause | keep his words on poking and on keeping the bridge busy. Move the section numbers with care: code cites them | about 45 lines |
| **Two count lines of the scratch cleaner** (F), `src/RimMandrake/Utils/scratch_reap_sanity.json` `end.refused`, `end.session_stale` | alarm when more than 60 scratch folders are kept | incident `disk-20261115210535` stays open on them since 2026-11-15, 17 revisits. Kept bytes are 1.0 GB; 506 GB is free. Operations proposed the cut on 2026-11-21. No danger is named (§No limit without the danger it guards) | the byte line and the disk line stay | 2 lines, 1 incident |
| **Open items about deleted things** (F): `RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM`; `SLOTS_RENAME_FOUNDRY_KEY_RELENTLESS_READS_IT` beside `RIMMANDRAKE_RETIRE_FOUNDRY_SLOT_KEY_INDEX_NAMED_A_GHOST` | review `relentless.py`; rename one slot key twice | `relentless.py` was deleted at `d2a0462048`. The two slot items name the same rename | the review item also names `ops_watch.py`; those files have their own rule now | 2 items to end |
| **The maturity dashboard, goal sheet and hub page** (G), `project_maturity_dashboard.py`, `infrastructure/state/GOAL_SHEET.md`, `infrastructure/dashboards/hub/` | read hand-ticked goals and draw a page | `GOAL_SHEET.md` last scored 2026-09-10. Hub data files are from 2026-10-02, except `health.json`. No timer runs the dashboard | `CONDUCTOR_GOALS.md` and the Maturation page replaced it [guess ~85%]. `conductor.md` line 57 names `GOAL_SHEET.md` to say that it is different; `codebase_health_publish.py` writes hub `health.json` | 1,176 + 291 + about 200 lines, 10 hub files |
| **State files of August to October that nothing cites** (G), `infrastructure/state/`: `IDEOLOGY_REBUILD_TRIAL.md`, `WORLDGEN_RUN.md`, `REBOOT_HANDOFF_2026-09-02.md`, `BENCH_HANDOFF.md`, `WORLDPAINT_REHEARSAL.md`, `LOAD_PROCEDURE.md`, `haiku_census_2026-10-31.md`, `live_proof_triage.tsv`, `lightspeed_unmatched.tsv` | old handoffs, a worldgen run book, old tables | 0 hits over `CLAUDE.md`, `skills`, `src`, `.claude`, seat files and the standing rulings (probe: `CANONICAL_SAVE.md` gives 6+). `WORLDGEN_RUN.md` describes worldgen, which is ruled out | git keeps them. Read each once for a lesson first. `WORLDPAINT_REHEARSAL.md` can matter for the one paint at the end: read it before it goes | 9 files, about 86 KB |
| **Root and manual leftovers that nothing loads** (G): `final.md`, `claude_sha.txt`, `.bridge.eld`, `GLOBAL_CLAUDE.md`, `infrastructure/agents/POLICY.md`, `REP.md`, `infrastructure/README.md`, `REFRESH.md`, `infrastructure/state/queue/HUMAN.md`, `src/RimMandrake/rimflow/docs/` (5 files), three `CODEX_PROPOSAL_*.md`, `Fable_Review/` (9 files) | old mirrors, superseded seat files, a 2026-08 inbox, a manual of an older rimflow | dates: 2026-08-14 to 2026-11-19; `HUMAN.md` last changed 2026-08-26. The 2026-11-19 census listed seven of them, and no run has deleted one. A citation is a test list, an inventory or another leftover | first edit `selftest_documented_commands.py`, `guiding_prose.json`, `entrypoint_inventory.py`, `STRUCTURE.md`, Charter §Queue (`HUMAN.md`) and one line of `generating-rimworld-sprites`. Move the Codex proposals to `design/RimMandrake/`; they are a design record | about 25 files, 1,299 lines in `docs/` alone |

## 3. Table 2: RETIRE, on his own words (he decides)

Each question stands alone. "Recommended" is this census's answer. Sizes are after the question.

1. **The Producer role** (class A). It wrote the plan and the cut lists. Last run: 2026-11-01. Operations has sent it 7
   forecasts since 2026-11-05; it answered none. You told us on 2026-10-29: *"I think calling the Producer once a week
   for planning is not at all the entirely of Producer. It also needs to track that schedule (relative to the stats
   from Operations, Foundry, etc.) and make a daily plan to follow as well."* On 2026-11-22 you ruled that the pipeline,
   not a seat, works the list. **Question: may we retire the Producer, and send the forecasts of Operations to the
   Conductor?** Recommended: yes. Size: `producer.md` 242 lines, the schedule row, off-switch tests, lines in
   `operations.md` and `conductor.md`, the `roles.Producer` and `tokentalk.role.producer` readings.
2. **The Auditor role** (class A). It sampled closed work each day. Last run: 2026-11-01. You told us on 2026-10-29 to
   give it the weekly lessons work (*"The Auditor once a week"*, item "Give the Auditor the lessons broom"), and on
   2026-10-29 *"Planted faults should be added from outside the system (I would suggest Auditor by its very design)."*
   **Question: may we retire the Auditor role and keep only its no-AI check of every closed item?** Recommended: yes.
   The daily findings judge, the weekly follow-through reader and Crystallize now do most of its work [guess ~75%].
   The no-AI check is in Table 3. Size: `auditor.md` 321 lines, 3 programs (`audit_prescreen.py` 349,
   `audit_hardflag_file.py` 217, `audits.py` 162), 4 tests. `close_audit.py` stays: `evidence_gate.py` uses it.
3. **The Artist role** (class A). It has never run: the launch records hold no Artist run, and `art_style_memory.md`
   has not changed since 2026-11-01. You said on 2026-11-01: *"The Artist. Responsible only for art generation.
   Reports to the Conductor. Oversees the Art pipeline. Already exists today as "an opus judge" in the existing
   pipeline."* The art judge and the art brief work without this role. **Question: may we retire the Artist role file,
   and keep its style memory as a reference for the art judge?** Recommended: yes. Size: 133 lines, the row, 1 test.
4. **"The system first", from the retired Relentless** (class D). You said on 2026-11-03: *"Relentless fixes operations
   or conductor or designer or any other part of the system before continuing content creation yes."* Both build items
   were dropped (2026-11-16 and 2026-11-18). No part of the pipeline reads the health verdict. Your 2026-11-19 ruling
   "No mod runs forward on a broken pipeline" does the same job per mod. **Question: does the 2026-11-19 ruling replace
   the 2026-11-03 rule, so that we may delete the health verdict?** Recommended: yes. Size: 43 lines in
   `standing_rulings.md`, `ops_health.py` 546 lines, 5 tests, 1 open item.
5. **The token throttle bands** (class D). The bands GREEN, AMBER, RED and FLOOR are still computed, and since
   2026-10-28 each band acts like GREEN. You said then: *"Stop the whole account rated RED on runeway crap. Just do the
   checkout."* On 2026-11-02 you made token limits advisory: *"Nothing gets killed or stopped for that."* **Question:
   may we delete the bands?** Recommended: yes; the account levels stay. Size: about 15 lines in `operations.md`, the
   band blocks and code in `role_launch.py` (lines UNMEASURED).
6. **The nightly full sweep of FlowWorks on SteveDesktop** (class D). Each night at 1:30 AM the timer `testq-sweep`
   queues every FlowWorks live check. Last night: three jobs, about 4.2 hours of planned time. You said on 2026-11-15:
   *"Nightly tests should check mods with finished versions, not mods in production. Code is too fluid otherwise. Wrong
   phase."* On 2026-11-21 you ruled that after a change only the touched checks run again, and that a full pass is a
   named act. The older ruling of 2026-10-25 allows one full sweep a day. **Question: may we stop this nightly sweep,
   and let a finished mod have one instead?** Recommended: yes. It also frees SteveDesktop. Size: 1 timer, 1 sentence.
7. **"Live runs are targeted" of 2026-10-25** (class D). Your words: *"Targeted runs should always have been policy."*
   The ruling of 2026-11-21 (§After a change, only the checks that the change touches run again) says the same, wider.
   **Question: may we merge the two into the newer one, with your words of both dates?** Recommended: yes. Size: 14
   lines. `focused_testing_plan_2026-10-25.md` goes with it.
8. **Two rulings of 2026-11-05 with one meaning** (class D): §The pipeline never "blesses" a small change, and §Fix it
   and check it yourself. Your words: *"The pipeline is NOT to be used to "bless" any change in the game."* and *"We
   MUST stop this endless token burn by making little cute notes on tickets"*. §Touching code has a cost (2026-11-19)
   covers both. **Question: may we put both quotes under "Touching code has a cost" and end the two sections?**
   Recommended: yes. Size: 30 lines; the Charter points at them.
9. **The daily agent-improvement pass** (class E). Each morning models read the day's evidence and propose edits to
   role files and skills. It made two edits, both for 2026-11-01 and 11-02. In the 20 days since, none was applied, and its
   first target each day is still "relentless", which is deleted. One run crashed on that (2026-11-22). You said on
   2026-11-02: *"Every day we should ask if each agent can be improved based on our evidence."* **Question: may we stop
   the daily pass, because the weekly Crystallize and the fresh-context skill sessions do this work?** Recommended: yes.
   If you say no, it goes to the revive list: remove the dead target, and find why it applies nothing. Size: 1,034 lines,
   1 timer, its state folder, its tests.
10. **The codebase-health page builder** (class A). Every 15 minutes it can rebuild an older clean/dirty page. You set
    its pace on 2026-09-04 (*"no more than every 15 minutes, to avoid unnecessary pauses"*). By card on 2026-11-19 you
    had the new CODEBASE_NOW page made, and it is one of your tabs. **Question: may we stop the old page builder?**
    Recommended: yes, after the two pages are compared once; `codebase_health.py` stays, because the new page reads it.
    Size: `codebase_health_publish.py` 286 lines, 1 template, 1 timer.
11. **Daily new-skill cards to you** (class E), `conductor.md` step (g). You said on 2026-10-29: *"This is a good thing
    to discuss with the user and a positive outcome."* The record shows 2 such notes, the last on 2026-10-29.
    **Question: shall skill proposals come to you only in the weekly Crystallize report?** Recommended: yes. Size: 12 lines.

Already in front of you from another run today, so not repeated here: the night reserve, the Codex review stop, the
checks of a cleansed design, and who decides Polish (`design/specs/2026-11-23-his-quotes-checked/questions.md`).

## 4. Table 3: REVIVE (promised, and silently not happening)

| what the rules promise | what the record shows | the smallest repair |
|---|---|---|
| **Every close is checked by a no-AI program** (`auditor.md` "Coverage by program") | `D:\ClaudeWork\rimmandrake\auditor\prescreen.json` was last written 2026-11-01, because only an Auditor run starts it. Every close since then had no pre-screen | run `audit_prescreen.py` and `audit_hardflag_file.py` on a clock of their own, then retire the role (question 2) |
| **Finished art renders are judged without an agent remembering to** (`rm-arteval-autojudge`) | the last real judgement was 2026-11-08 10:38 AM. In the last 3 days: 21 passes refused "allocator N=0", 14 judged 0. 86 follow-ups wait, some since 2026-10-28. Today's status also reads "commit failed ... regen_rounds.json left uncommitted". His 2026-11-02 order made token limits advisory, and his card of 2026-11-07 ("Judge, install, redraw") works only when the environment variable `ARTEVAL_AUTOJUDGE_CARD` is set; no unit on this machine sets it. He put art after FlowWorks (2026-10-18), so the cost is low today | decide with the Conductor if the timer is paused in words, or the N=0 gate and the commit are repaired. Today it does neither |
| **Operations' forecast leads to a plan change** | 7 `REPLAN REQUEST` notes from 2026-11-05 to 11-21. `CUT LIST`: 1, on 2026-10-29. No reader | already filed: `RIMMANDRAKE_ROUTE_REPLAN_REQUESTS_TO_CONDUCTOR_PRODUCER_OFF` |
| **An alarm reaches his phone by a route that rings** (§Todoist is for to-do lists only: "until the new alert route is built, no alarm reaches his phone") | off since 2026-11-19. The design item is proposed, unchanged since 2026-11-19; `RIMMANDRAKE_CARD_PHONE_ALERT_ROUTE_AFTER_PUSHOVER_FACTS_CHECKED` is in progress; a `pager.py` exists on main | finish that card item; he picks the route |
| **Each hand act on the pipeline is folded within a day** (`conductor.md` §Builds) | 106 acts on record, 18 open, 11 overdue, the oldest 61 hours. The incident `maturation-20261121225203` stays open on it. So the rule is mostly followed (88 folded) | the hand-launched helper should carry its `why` at launch, so the fold is automatic (Operations names this cause each day) |

Also owed, and not a rule: **348 items sit in the states "built" (245) and "validated" (103) with no event since
2026-11-13**, the states that the retired pipeline's judge used to clear. 367 "proposed" items are as old. The ticket
sweeps per mod (Knockback, Pyrelands and FlowWorks, 2026-11-22) show the way. This is list work, not a retirement.

## 5. Table 4: looked at, KEEP

**Roles.** Conductor (103 launch files in 14 days), Operations (229), Designer (74, last 2026-11-21): alive. DesignerCodex: last
2026-11-16, inside 14 days, his words of 2026-11-15. Role briefs that programs load and that have current work:
`criteria_fixer`, `list_shape`, `walk_brief`, `fable_rescue`, `code_review`, `conductor_restart`, the eight Designer
packet files. `runner_options.md`: kept for DesignerCodex. The Arbiter is gone from the schedule; its name is left in tests and simulations.

**Root `CLAUDE.md`.** Each of the 49 sections was read once. None waits on a gone thing, except the build-pause pointer
(Table 1) and `V1.md` in "What is where" (last change 2026-08-23, still cited by a test: look at it when the paint is
planned). The line on the retired FOUNDRY seat is a correct mapping.

**`standing_rulings.md`** (all 67 headings looked at; those not in Tables 1 to 3 are KEEP). Notes on the near misses:
- Biome art never blocks: waits on FlowWorks, which is in the in-game stage. Alive.
- Account and capacity budget: its order was stale; another run corrected it this morning.
- Every mod's test script matures at first touch: corrected this morning. Two of its items (Baroque, Solar) are still proposed from 2026-11-04.
- Spare capacity and the conditional pass: corrected this morning; it no longer reads as a mod pass.
- Retest only after a code change, Test Pilot, Codex full access, wrap-up is a script, broken tests are expected: each has live code or a live use.
- No limit without the danger: its measure is due 2026-12-03.
- North-star validation state: the 2026-09-18 counts are a record of a wrong alarm. Keep until `doctor` changes.
- Draw order: built, but its item `RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES` still reads proposed.
- Conductor authority: one rule, restated as a pointer in the Charter and each role file. Each copy is a pointer; keep.

**Hooks** (34, 30-day refusals in 10,808 transcripts). Alive: `block_blanket_git_stage` 2,282 · `block_tmpfs_clone` 262 ·
`block_shared_tree_merge` 206 · `block_unbounded_agent` about 275 · `block_agent_over_slots` about 200 · `block_blind_scan` about
190 · `block_ledger_lint` about 80 · `block_hand_edited_sheet` about 80 · `queue_lint` about 75 · `block_forged_validation` 33 ·
`block_unbounded_robocopy` 25 · `block_agent_coded_name` 22 · `role_result_before_stop` 20 · `block_unledgered_texture` 19 ·
`block_worktrees` 18 · `block_orphan_item_prose` 17 · `block_owner_doc_wsl_paths` 14 (called from another hook) ·
`block_delegated_cards` 9 · `block_canon_contradiction` 1 · `auto_allow_bash_permission` log to 2026-11-22 · `switch_checkpoint_signal` 48 ·
`conductor_goodbye` 35. The small ones rest on exact text matches, so each count is a floor.
`warn_skill_unwired`: its name appears 114 times in 51 transcripts; how many are real warnings is UNMEASURED; it skips skills listed as not registered.
Zero refusals in 30 days, kept because the danger is live and the hook is cheap: `block_agent_without_model` (his Haiku
ban; a user-level hook overlaps it), `block_send_to_restarting` (101 restarts on record), `block_paste_handoff` (his
standing rule), `block_dll_source_mismatch` (also a git pre-push check; DLLs are still committed).
Not refusal hooks, in use: `capture_card_answer`, `handoff_restart`, `run_end_wake`, `set_session_title`, `wrapup_hook`.

**Timers.** 49 listed. Ours not in a table above fired in the last day. `rm-artpipe-idle-fill` answers NOTHING_OWED, as
its art is after FlowWorks. `rm-fleet-now` and `rm-running` are live pages with an old file name (RELENTLESS_NOW.md;
its name is kept because readers open it). `rm-restart-now` still prints "FOUNDRY stamp spent: removed"; `/home/mandrake/rm/foundry` is an empty folder.
`rm-canon-sweep`, `rm-findings-judge`, `rm-deadman`, `rm-vv-matrix`, `rm-objstore`, `rm-order7`, `rm-control-acts-export`: each has a reading from today.
`rm-streams-collect`: fires every 15 min; its page reader was not traced.

**Open incidents** (10). Two are in Table 1 (plan, disk), one in Table 3 (maturation). The other seven read a live
fault or a real load: flow, accounts, dispatcher, testing, timers, steve, work_belt.

**Process files.** `delegation_policy.md`, `CHARTER.md`, `Agent_Policy.md` (beyond the items above): no dead clause found.
Two false paths met: `Agent_Policy.md` lines 177 and 290 name `fleet_refresh.py`, which is not on main.
`using-rimflow` is current. The delegated digest is built each day (today's is in `/home/mandrake/rm/bench/Transient/`).
Flagged files: 5, the oldest from 2026-11-21, so the weekly examination is not yet late; the Friday judge is still not
wired to do it (`RIMMANDRAKE_WIRE_FRIDAY_JUDGE_TO_EXAMINE_FLAGGED_FILES_WEEKLY`).

**State files that code still cites, kept:** `V1.md`, `V1_CHAIN.md`, `LIVE.md`, `OWNER_DECISIONS.md`, `RELOAD_CHECK.md`,
`WORLDGEN_FACTION_CHECKLIST.md`, `EXPECTED_FAILURES_next_load.md`, `TEST_PLAN.md`. Each is 1 to 3 months old. The
next look can ask whether the citing code is alive.

## 6. Could not look

- Selftests that guard a dead thing: UNMEASURED. No per-test log of reds for 30 days was read; the tests of each candidate are in its row.
- Stop and UserPromptSubmit hooks leave little trace in a transcript. A zero for `block_paste_handoff` is weaker than a zero for a PreToolUse hook (probe: `role_result_before_stop`, also a Stop hook, shows 20).
- Transcripts that were deleted before this run: not in the count. SteveDesktop and the Macs: not scanned.
- The dead part of `dispatcher.py` and the band code in `role_launch.py`: lines UNMEASURED.
- `src/RimMandrake/Utils/sim/` (24 files, 9,306 lines, some simulate retired roles; last change 2026-11-22): not read.
- 547 lessons, 26+ boundary pages, 144 skill files, `conversations/`: outside this pass. A lesson that names a retired thing is not counted.
- Who reads `rm-streams-collect`'s page; whether `STATUS_BOARD.html` (written 9:03 AM today) has a reader: not traced.
- The exam and judge briefs in `design/concepts/`: not looked at.
- Whether he still opens the old codebase-health page: only he knows.

## 7. What was done (2026-11-23, item `RIMMANDRAKE_DECIDE_RETIRE_CENSUS_EIGHTEEN_ARE_THE_CONDUCTORS`)

The Conductor decided: every row of Table 1, and rows 4, 5, 6, 7, 8 and 10 of Table 2. The removed paths, units and words
are in `selftest_retired_era_gone.py` (`RETIRED_PATHS`, `RETIRED_UNITS`, `RETIRED_WORDS`). Set down, each with its evidence:
- `rm-dispatcher.service`: `seat_restart.py` (2 places) and `rm-restart-now.service` start it. Only its timer went.
- The ring itself (`dispatcher.ring`, `caps`, `no_handoff`, `doorbell.py`): `incident.py` gives a ring `how: doorbell` by
  default, and `incident_execute` sends it; `no_handoff.conductor_log` is the live path of every RAISE FIRST line.
- `steve_cpu_retest.py`: `soak_read.py` and `steve_cpu_sweep.py` import it. Its timer, its units and its copy on D: went.
- `focused_testing_plan_2026-10-25.md`: seven files of `modcheck` cite it as their design.
- The close pre-screen and the reader of Operations' proposals: the run
  `RIMMANDRAKE_REVIVE_FIVE_PROMISED_THINGS_SILENTLY_NOT_HAPPENING` rebuilt the first (`close_check.py`,
  `rm-close-check.timer`) and holds the second.

Candidates seen on the way, for the next census:
- `alarm_item` in `dispatcher_schedule.json` is `RIMFLOW_V3_BUILD_DISPATCHER_FIRST`, an item that is dropped.
  `OPERATIONS_MONITOR_ACCOUNTS_OFF_SHARED_TABLE`, the note home of Operations, is done.
- Two live promises watch `series/relentless.jsonl`, last written 2026-11-18. One item of them reads broken
  (`CHECKER_DEATHS_ALARM_BUILD_29_WENT_UNHEARD`).
- `owner_pause.json` and `run_rules.json` still describe the retired `relentless.py` as their reader.
- The state machine of `steve_cpu_retest.py` (arm, tick) and its selftest: no clock runs it.
