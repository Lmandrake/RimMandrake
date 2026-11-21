# BENCH_REBOOT_HANDOFF_202611210050 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611202347`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
**NIGHT ORDER IN FORCE, ends when he next writes.** Order (owner, Fri 2026-11-20 3:53 PM PST): "I am about to go AFK for the rest of the night. I'd like you to be very productive without my presence... We should be burning on two mods at the same time, flow works and something else. Make sure the account switchover is scheduled and set up to not destroy work this time. Pipeline repairs hopefully have top priority (the SIGNIFICANT changes as we agreed to)." 4:00 PM: "please leverage CODEX for art and code reviews richly, it has a lot of capacity left." About 4:15 PM: "Steven has just authorized us to use his account FULLY as the next act... we do NOT switch to lukas.mandrake next, we switch back to Steven and burn it as fully as we safely can. This also allows us to work on three mods at once so long as the pipeline can handle that and there's no indication it's breaking again. I leave it to you to monitor it, ok?" then "Do not switch right now! Use up this account first ok?" and "Of course you should raise it to 3% to give them room to finish towards 1%. Otherwise you're ensuring lost work." and "You're using a LOT of subagents rather than detached processes. Be careful of your context... You're going to need to be a mindful orchestrator tonight." So: three mods run (FlowWorks, GimmeSomeSlack 0.1.1, Pyrelands); you WATCH the pipeline and repair it when it stalls; every new job is a DETACHED run (`detached_helper.py launch`, repair runs with `--env RM_CONTROL_MOD=none`), never an in-window helper; read only final reports. The account switch system -> steven happens by itself when system reaches 3% (plan exception SYSTEM_THEN_STEVEN_TO_FLOOR_2026_11_20; notice has been pending since 4:50 PM PST); do not switch or kill by hand.

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **SteveDesktop:** the hypervisor-off boot (his card pick) ran and the machine is back to normal. Result: FAULT SEEN with the hypervisor off, 3.5 min after the game started, same as with it on. The hypervisor is not the cause; left are the ASUS/Corsair/ENE drivers or the CPU itself. The trigger is the game running, not CPU load (66 h Prime95 soak: 0 bad in 527 cycles). Evidence `D:\ClaudeWork\rimmandrake\conductor\night_20261120\steve_hypervisor_test.md`. Next test (drivers unloaded) is his hardware: bring it to him with this result.
- **The art queue is down:** its worker accounts for the Codex image tool lost their sign-in on 2026-11-10; every queued job fails. Signing in is an interactive login, his. Tonight's art went one at a time on the shared Codex account.
- **Vanilla electrical art:** design done (`D:\Luke\dev\RimMandrake\design\specs\2026-11-20-vanilla-electrical-art-home\design.md`): Gimme Some Slack keeps wiring and lights, a new mod Machine Looks takes appliances and workbenches; the Conductor put the fridge art there (his "your call"). No review sheet exists; the one vanilla-electrical-looks sheet copy of 2026-11-20 in the Transient biome sheet folder is WRONG (shows a suit charger as the battery), never serve it.
- **Version tags are policy and live:** `mod/GimmeSomeSlack/v0.1.0` is on origin at e1d9c3c042; the pass step tags by itself now.
- **Changes he can veto:** max_live raised 1 -> 3 on his word, then 3 -> 4 as the Conductor's act while a repair run holds a mod slot; Pyrelands blind-cycle counts reset to 0; Pyrelands switched ON (ct_000083).
- **FlowWorks true cause, owed to him in plain words:** the pipeline only wrote the game-only exit as a hand command and never ran it (515 minutes parked). Fixed in cdfab28b7b.
- Biome open questions page `D:\ClaudeWork\rimmandrake\conductor\biome_open_after_picks_20261120.md` is STILL unread by the Conductor. No cards are open. No drafts await his word.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_REFUSE_STAGE_THREE_BAR_READS_NO_BUILT_FILE` — the repair run built the check as specified, it flagged 25 of 49 bars of the passed GimmeSomeSlack, and the run reverted it; evidence in the ticket note; NEXT: launch a detached Designer-level run to pick a different signal, or drop the ticket with that evidence. (owed: `RIMMANDRAKE_WORK_NIGHT_POINTERS_OF_NOV_TWENTY_SWITCH_HANDOFF`)
- `RIMMANDRAKE_RESIGN_PYRELANDS_COVERAGE_AFTER_RESTAMP_VOIDED_IT` — detached Opus run launched 4:44 PM PST, wakes the seat (it read 'deactivating' at 4:50 PM); NEXT: read its result and confirm with `maturation.py next` that the Pyrelands Stage 4+5 exit no longer refuses on coverage.
- `RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES` — fix published (ac9a5418ce); the close waits for the 1:30 AM PST firing of testq-sweep.service; NEXT: after 2:00 AM PST read `systemctl --user status testq-sweep.service` and close it with its `--live` promise if green. (owed: `RIMMANDRAKE_WORK_NIGHT_POINTERS_OF_NOV_TWENTY_SWITCH_HANDOFF`)
- `RIMMANDRAKE_FIX_FLOWWORKS_FAULT_LOOP_AND_SLACK_STEWARD_MISREAD` — at 4:55 PM PST FlowWorks read system_fault (three refused launches of the pits fixer) and GimmeSomeSlack read steward_spent while its steward run read running; a detached Opus repair run is launched on both; NEXT: read its result when it wakes you and confirm with `./pipe show` that both mods have a live run.
- `RIMMANDRAKE_RELEASE_STAGE_CEILINGS_WHEN_THREE_MODS_REACH_THEM` — the three mods run: Pyrelands blind cycle 4 live (judge run), GimmeSomeSlack 0.1.1 preflight steward live but its tick line read `steward_spent` while the run was still live, FlowWorks pits fixer was waiting for a slot before max_live went to 4; NEXT: run `./pipe show` and `./pipe why <Mod>` WHOLE for the three, fix whatever stalls with a detached run, and release a stage ceiling (25M weighted tokens each, spend UNMEASURED) with its spend logged when one is hit.
- `RIMMANDRAKE_SPLIT_SECOND_GAME_MODS_FOLDER_SHARED_WITH_FIRST` — detached Opus run still live, counted as a GimmeSomeSlack slot; NEXT: read its result when it wakes you, then set max_live back to 3 in `src/RimMandrake/rimflow/maturation_dispatch.json`. (owed: `RIMMANDRAKE_WORK_HANDOFF_POINTERS_OF_NOV_TWENTY_SITTING`)
- `RIMMANDRAKE_LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART` — not launched; NEXT: launch one detached run that sends the GimmeSomeSlack 0.1.1 fixes and the FlowWorks pits rebuild to Codex (`gpt_consult.py`) for review once each lands, mod code and art only, never pipeline machinery.
- `RIMMANDRAKE_SEND_STEVE_FLOWWORKS_CHECKS_AFTER_HYPERVISOR_TEST` — SteveDesktop is restored and its lane resumed; not submitted; NEXT: submit the FlowWorks game-only checks to its lane with testq (results tagged as from a faulty machine) after the pits fixer lands.
- `RIMMANDRAKE_BURN_STEVEN_FULLY_NEXT_NOT_LUKAS` — plan exception live on origin (system to 3%, steven to 3%, then lukas); NEXT: after the switch, run `switching_plan.py status` and `account_usage.py now`, confirm steven is live, and close it; delete the exception when Steven's reset is used.
- `RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY` — filed, not launched (three mods already run); NEXT: admit the mod when a slot is free, battery first, fridge art folded in. (owed: `RIMMANDRAKE_WORK_NIGHT_POINTERS_OF_NOV_TWENTY_SWITCH_HANDOFF`)
- `RIMMANDRAKE_JUDGE_SLACK_COVERAGE_AGAIN_UNDER_CALIBRATED_BRIEF` — filed by the helper that opened 0.1.1 (his card of 2026-11-16: judge coverage again when the next version opens); NEXT: launch it as a detached blind coverage-judge run with its launch-checks block. (owed: `RIMMANDRAKE_WORK_HANDOFF_POINTERS_OF_NOV_TWENTY_SITTING`)
- `RIMMANDRAKE_CARD_STEVE_HYPERVISOR_TEST_FAULT_IS_FREQUENT_AGAIN` — test done, result on the item; NEXT: tell him the result in the morning summary and card the driver-unload test with `RIMMANDRAKE_RERUN_FAULT_WINDOW_VERDICTS_ON_CLEAN_BOOT`.
- `RIMMANDRAKE_WORK_HANDOFF_POINTERS_OF_NOV_TWENTY_SITTING` — the earlier handoff's unstarted pointers stand: `RIMMANDRAKE_ASSIGN_LEFTOVER_CONTEXT_CHANGES_NEITHER_WORKER_HAD`, `RIMMANDRAKE_CLOSE_FLOWWORKS_ITEMS_FIXED_IN_BUILD_STILL_PROPOSED`, `RIMMANDRAKE_READ_STEVE_RESUME_REPORT_CAN_FILL_RAISE_NOISE`, `RIMMANDRAKE_NAME_STAGE_CEILING_DANGER_OR_REMOVE_THE_LIMIT`, the biome page read, seven open incidents; NEXT: launch the oldest two as detached runs once the three mods are seen moving.

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- Seven in-window helpers in one seat clone made an unrelated publish refuse on a half-edited brief; night work goes out detached (filed: lessons)
- A repair run without `--env RM_CONTROL_MOD=none` takes a mod's max_live slot (filed: lessons)
- A grep on `rimflow file` output hides a refusal; two files were silently refused (filed: lessons)
- The switch timer read a stale 2026-11-05 week plan file, so no edit to switching_plan.json took effect until a helper removed it (see: D:\ClaudeWork\rimmandrake\conductor\night_20261120\account_switch_safety.md; three lessons filed by that helper, 47e044e556)
- The ledger push hook linted a tag's older commit against origin/main and refused the push; fixed 0fe80361702d (see: selftest_block_ledger_lint.py)

## Closed since the last handoff (12)

- `RIMMANDRAKE_SORT_SLACK_WALK_INTO_PATCH_AND_NEXT_VERSION` — f4203845661a
- `SELFTEST_FIX_GSS_ART_MANIFEST_SIZES_SLAT` — ea55afcea321c4521e91d44af562c707a881f984
- `RIMMANDRAKE_FIX_LEFT_OPEN_PARSE_READS_ITS_OWN_DENIAL` — a15619f150a545705a02a582220095fb6ce6d7bf
- `RIMMANDRAKE_LAND_CLOSED_PROSE_MOVE_HELPERS_PUBLISH_SHARD_ONLY` — 922ce3fc1fbca25c89a68835c9bd74a4f2246328
- `RIMMANDRAKE_RESTAMP_PYRELANDS_CONCEPT_TREE_RED_IN_TWO_LANES` — 47e044e556df
- `RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART` — 37d95a84481c3685077c2f9a0d0585184a6ae967
- `RIMMANDRAKE_FIX_STAGE_CEILING_ARRIVAL_TEST_RED_ON_MAIN` — 5f1df790a8
- `RIMMANDRAKE_UNPARK_FLOWWORKS_STUCK_AT_OFFLINE_STAGE_EIGHT_HOURS` — a79ad5e7bb
- `RIMMANDRAKE_KEEP_RUN_REPORT_WHEN_LATE_REMARK_FOLLOWS` — 07b78ded245aac235374c8655f30c5c0fae5d954
- `RIMMANDRAKE_PUBLISH_THREE_PERCENT_LEAVE_LINES_BEFORE_EIGHT_PM` — 6e06e45588
- `ACCOUNTS_RESTORE_STEVE_LINE_AFTER_BIG_WEEK` — done by verify, no close
- `RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT` — done by verify, no close

## Filed and still open (20) — the next seat's queue

- `RIMMANDRAKE_SEAT_SLACK_CORDS_IN_OFF_SWITCH_NOT_CUT` — Gimme Some Slack 0.1.1: an off switch draws its cords as cut ends; they should read connected without power (the off switch is in no power net, so it 
- `RIMMANDRAKE_LOAD_SLACK_POLE_ICONS_ON_MAIN_THREAD` — Gimme Some Slack 0.1.1: Link wire, Unlink wire and Unlink all show the missing-texture square; their vanilla icons load off the main thread and stay n
- `RIMMANDRAKE_DRAW_SLACK_POLES_IN_FRONT_WHEN_SOUTH` — Gimme Some Slack 0.1.1: a power pole south of something draws behind it (masts print on the Building layer, under plants and BuildingOnTop things)
- `RIMMANDRAKE_BLOCK_SLACK_ROOF_OVER_POLE_KEEP_THE_CUT` — Gimme Some Slack 0.1.1: a roof can still form over a standing power pole (auto-roof, build-roof); block it, keep the roof cut in code
- `RIMMANDRAKE_WIRE_STYLE_ICONS_INTO_EVERY_LOOK_MENU` — Next version (Divergent), Gimme Some Slack and FlowWorks: every four-looks menu shows one proper icon per look, from one shared piece (_Shared/StyleIc
- `RIMMANDRAKE_STYLE_SLACK_BATTERY_LIKE_THE_LAMP` — Next version (Divergent), Gimme Some Slack: the battery takes the four looks and follows its run, as the standing lamp does (code; art ordered on RIMM
- `RIMMANDRAKE_CUT_SLACK_REVIEW_STATIONS_NOBODY_READS` — Next version, Gimme Some Slack: delete the review stations no check or walk reads (proposed 5, 8, 9, 11, 17, 18, 19, 23, 27, 30) and the KNOWN GAP lin
- `RIMMANDRAKE_ADD_FRIDGE_ART_TO_ELECTRICAL_RESKIN_HOME` — When the vanilla electrical art design pass reports: add the fridge art to that mod's scope and file its art item (art gathered out of the main pool);
- `RIMMANDRAKE_SEND_STEVE_FLOWWORKS_CHECKS_AFTER_HYPERVISOR_TEST` — After SteveDesktop is restored from the hypervisor-off boot: submit the FlowWorks game-only checks to its lane (testq), results tagged as from a fault
- `RIMMANDRAKE_LAUNCH_CODEX_REVIEWS_OF_MOD_CODE_AND_ART` — Tonight, on his word of 2026-11-20: launch Codex reviews of mod code (Gimme Some Slack 0.1.1 fixes, FlowWorks pits) and of the art sheet; never pipeli
- `RIMMANDRAKE_BURN_STEVEN_FULLY_NEXT_NOT_LUKAS` — Owner 2026-11-20 about 4:15 PM PST: the next account is steven, not lukas, burned as fully as is safe. Change switching_plan.json (steven leave line 5
- `RIMMANDRAKE_RUN_TARGETED_CHECKS_PAST_UNBUILT_MUST_SHOW_LINES` — An uncovered must-show line refuses every modcheck run of the mod, targeted ones too: FlowWorks frozen since 82e59b2d76, testq-sweep failed
- `RIMMANDRAKE_JUDGE_SLACK_COVERAGE_AGAIN_UNDER_CALIBRATED_BRIEF` — Gimme Some Slack 0.1.1 is open, so its coverage is judged again under a coverage brief that reads CALIBRATED (his card 2026-11-16 point 19: 'Leave the
- `RIMMANDRAKE_RELEASE_STAGE_CEILINGS_WHEN_THREE_MODS_REACH_THEM` — Tonight: when FlowWorks, GimmeSomeSlack or Pyrelands reaches its stage spend ceiling, read the spend (maturation_dispatch.py releases) and release, lo
- `RIMMANDRAKE_ADMIT_MACHINE_LOOKS_MOD_WITH_FRIDGE_AND_BATTERY` — Admit the new mod Machine Looks (design/specs/2026-11-20-vanilla-electrical-art-home/design.md): our four looks for vanilla electrical machines and wo
- `RIMMANDRAKE_RESIGN_PYRELANDS_COVERAGE_AFTER_RESTAMP_VOIDED_IT` — The Pyrelands concept tree restamp (47e044e556) voided the coverage signature: re-sign coverage and re-pin the exam, and bring design/concepts/Pyrelan
- `RIMMANDRAKE_ROUTE_FLOWWORKS_PAPERWORK_GAME_ITEMS_TO_VISIT_THREE` — FlowWorks: 5 open game-up items caused by RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD (COATING_WASH, BOTTLE_JOBS, DRILL_SURVEY, SHEET_DROW
- `RIMMANDRAKE_FIX_MATURATION_NOW_SELFTEST_PINNED_TO_LIVE_GSS` — selftest_maturation_now rows '7 agreeing files: no disagreement on GSS' and '7 a locked change back in the Designer' are red: they read the live Gimme
- `RIMMANDRAKE_FIX_CODEX_RUNNER_SELFTEST_CONCEPT_LANE_READS_EMPTY` — selftest_codex_runner test_concept_runner_and_lanes is red: the codex lane reads [] where [('/c/M','codex')] is expected; red on base 2026-11-20 4:45 
- `RIMMANDRAKE_REDO_MODERN_BATTERY_NORTH_VIEW_FAILED_JUDGE_THRICE` — The Modern-look battery is still owed: its north-facing picture failed the art judge three times for not matching the east view in size (design/specs/

## Commits

```
fbf97b2306 conversations: catch-up 1 record(s)
f10afa260b ledger: RIMMANDRAKE_RESIGN_PYRELANDS_COVERAGE_AFTER_RESTAMP_VOIDED_IT note
96ea92c2bf ledger: Steve hypervisor-off one-boot test result (FAULT SEEN with hypervisor off)
73567172f8 maturation_dispatch: max_live 3 -> 4 while a repair run holds a mod slot (Conductor's act)
e1133eb4cf Pyrelands stage.json: pending_decision drops the done restamp, names the Conductor's certify and the whole exam retake
defd3d2565 ledger: RUNNER ingest of 0 testq job(s)
df34c48f5b ledger: RIMMANDRAKE_FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET clone bundled
655ded1637 conversations: catch-up 1 record(s)
eab120961a ledger: detached run on RIMMANDRAKE_FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET ended
0c12cc62f2 ledger: Modern battery art owed item
61cdde98e6 ledger: RIMMANDRAKE_FIX_FILED_PIPELINE_TICKETS_AFTER_WEDNESDAY_RESET note; lesson on test-table reads
0905bf61f3 Pyrelands blind cycle 4: lane 1 recorded blind (25 PASS, 0 FAIL, 38 game-side UNSETTLED)
a559ab58d4 ledger: RUNNER ingest of 0 testq job(s)
de6ae92a06 ledger: RIMMANDRAKE_RESIGN_PYRELANDS_COVERAGE_AFTER_RESTAMP_VOIDED_IT filed
c08b3ae065 ledger: notes on RECALIBRATE_JUDGE_THEN_RESTAMP_PYRELANDS_ONCE (re-sign owed) and SWITCH_ON_PYRELANDS_AND_SLACK_WHEN_ROWS_CLEAR (Pyrelands ON, ct_000083)
07b78ded24 detached_helper: a late remark after a run's report no longer replaces the report
0a09d74503 ledger: RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART clone bundled
6e06e45588 conversations: catch-up 1 record(s)
b1ffd3a249 ledger: detached run on RIMMANDRAKE_DESIGN_HOME_FOR_VANILLA_ELECTRICAL_ART ended
d5a6c6bd48 ledger: RIMMANDRAKE_TAG_EACH_PASSED_MOD_VERSION_PIPELINE_DOES_IT verified L0 and closed at baf8496f38ad (per CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM)
... 50 more: git log --oneline 6eda6ef5fd..HEAD
```

## Game / bridge / tree state at wrap

- running   : RUNNING   (RimWorldWin64 running, bridge answers)
- recorded  : UP
- Bridge: FREE    since 2026-11-20T23:43:18Z

Uncommitted (replace the placeholder after each line below with whose it is —
yours, the other seat's, a subagent's):

```
?? infrastructure/state/items/RIMMANDRAKE_CARD_STEVE_HYPERVISOR_TEST_FAULT_IS_FREQUENT_AGAIN.md   (this window's: item prose written by the by-card note; commit it)
?? infrastructure/state/items/RIMMANDRAKE_SORT_SLACK_WALK_INTO_PATCH_AND_NEXT_VERSION.md   (this window's: item prose written by the by-card note; commit it)
```

