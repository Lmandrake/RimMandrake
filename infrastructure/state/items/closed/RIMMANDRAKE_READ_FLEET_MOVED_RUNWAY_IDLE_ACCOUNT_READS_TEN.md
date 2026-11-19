# RIMMANDRAKE_READ_FLEET_MOVED_RUNWAY_IDLE_ACCOUNT_READS_TEN

## What the card said

<!-- answered 2026-11-19T16:14:11Z; recorded by `file` (OWNER); written by rimflow, never by hand -->

**Question:** [owner-asked] Thu Nov 19, 8:07 AM PST. Hand-written in the Binding style; no tool has measured the wording. Operations is the scheduled agent that reads the health alarms and fixes or notes them. It costs about 4.6 million weighted tokens on a full day, 25 to 29 runs. 56% of that pays for the start package: the rule files, memory file and skill list each run loads before it reads its alarm. About half of the package has nothing to do with Operations. Each pick below makes one run cheaper. (Hard to read? Type STE, Binding or Both for a rewrite.) Which of these do I build?
**Picked:** Slim the start package (Recommended)
**Its description:** Why: it cuts every run, on either model, and the same change can later go to every role. Removes the skill list, your personal rule file and the memory file from Operations runs, and stops telling them they are the Conductor. Saves about 1.2 to 1.8M a day [guess]. Cost: small build, 1 day test; a rule only in your personal file is no longer seen.
**His words:** Slim the start package (Recommended), Trim waste inside a run, Sonnet for follow-ups only, "If we escalate to (4) then we would likely give Sonnet Escalation: recognize something is fishy, so call out Opus to continue."
**Other options:** Trim waste inside a run · Sonnet for follow-ups only · Sonnet for every run

**Question:** [owner-asked] The second way to cut Operations is fewer runs. It was planned as about 10 runs a day and makes 25 to 29. Of 105 runs, about 13 landed a real fix; 57 only wrote a note, and those 57 were 38% of the spend. Two causes: a bug that treats "the plan is one hour older" as news and starts a follow-up run each hour, and five alarms that always get the same "nothing to fix" answer (unclaimed SteveDesktop incident, low lukas runway, standing wrap-up debris, idle pipeline, scratch dirt). Which of these do I build?
**Picked:** Fix the news bug (Recommended)
**Its description:** Why: 11 of 42 follow-up launches were set off by a reading that only aged. A reading that just gets older stops counting as news. Saves about 0.5 to 1.0M a day [guess]. Cost: small build with its test; a real jump in those readings is caught one step later. Works well with the program-answers pick: together they are the plan the analysis advises.
**Picked:** Program answers 5 repeat alarms
**Its description:** Why: a sixth look at those five alarms found something new 0 times. A program writes the same note the agent wrote, and calls the agent only when a reading leaves a stated range. Saves about 0.5 to 0.9M a day [guess]. Cost: small to medium build, 2 days test; a later look that would have found something is lost.
**Picked:** Program follows open incidents
**Its description:** Why: the biggest cut in run count. A program re-reads each open incident's numbers and calls the agent only when one crosses a stated line; one deep Opus run a day stays. Saves about 1.0 to 1.8M a day [guess, low confidence]; it includes the news-bug fix. Cost: medium build, 2 to 3 days test; each incident plan needs a line a program can check.
**Other options:** Retire Operations

**Question:** [owner-asked] One more item saves no tokens. On Nov 17 the fleet stopped twice when the lukas account hit its floor. The page showed "runway 10" for the next account, because runway is computed from each account's own burn, and an unused account burns nothing. No reading said how long the next account would last once the fleet moved onto it. Only two choices here: the reading is built or it is not. Do I build that reading and a short-window burn alarm?
**Picked:** Build it now (Recommended)
**Its description:** Why: it is the reading that would have warned of both Nov 17 stops, and it is a program, so it costs no tokens to run. Applies the fleet's measured burn to each account it could move to, and alarms on a fast burn inside a few hours. Cost: one detached build run and its tests.
**Other options:** Not now

**Owed by this card** (the close names where each was done or filed): needs a line a program can check

Source: D:\ClaudeWork\rimmandrake\conductor\operations_role_analysis_20261117.md (filed from the owner's card answered ~8:10 AM PST 2026-11-19, recorded on RIMMANDRAKE_EXPLORE_OPERATIONS_OPTIONS_AFTER_WEDNESDAY_RESET). Filed by a Conductor helper; paperwork only, nothing built.

## spec

Card pick: "Build it now" (the third question). Analysis section 3 ("What it missed: the two fleet stops on 11-17 (03:35 and 05:50)") and section 4 item 4.

Today src/RimMandrake/Utils/ops_watch.py `runway()` (line 356 at ba23c55414) is weekly quota left / (that account's own burn rate x hours to reset), capped at 10. An account not in use has rate 0 and reads 10 by construction; the reading models no 5-hour window and no "if the fleet moved here". A short-window burn of 6 points in 2 h on the live account (lukas) did not surface for the next account.

Build, in ops_watch (deterministic; no LLM):
1. A fleet-moved runway per candidate account: that account's quota left, divided by the fleet's measured burn (the live account's slope, slot_allocator.slope / account_usage readings) x its own hours to reset, for every account the switching plan could move the fleet to.
2. A short-window burn alarm: a fast burn over a few hours on the live account, against the next account's room.
3. Rules in src/RimMandrake/Utils/ops_watch_rules.json and routes in src/RimMandrake/rimflow/alarm_routes.json for both readings; digest.md shows the moved runway beside the plain one.

## verify

Acceptance test: a replay selftest written with the code, src/RimMandrake/Utils/selftest_ops_watch_fleet_runway.py, built from the recorded account readings of 2026-11-17:
- the moved runway or the short-window alarm fires before the 03:35 stop (1) and before the 05:50 stop (1);
- an idle candidate account does not read 10 when the fleet's burn would empty it before its reset (1);
- a quiet day's readings raise no alarm (1).
Expected `4 of 4`. Watched it fail on main ba23c55414 in the only way it can today: the file does not exist (`ls: cannot access ... No such file or directory`). Plus every existing ops_watch selftest that reads the accounts sense or the rules file, run after each change.

## criteria

- Replay selftest 4 of 4; the ops_watch selftests touching accounts and rules are no worse than before.
- Touches ops_watch_rules.json: the close needs `--live`, e.g. `--live "unit=rm-metronome.timer reading=D:\ClaudeWork\rimmandrake\ops_watch\status.json max_age=2h"` with the new reading present in status.json.

## Close note

The card stamps one owed line on every item it decided: "needs a line a program can check" (from the incident-clerk option). It is RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED's work. A close of any other item names it, e.g. `--why "a line a program can check: filed RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED"`, or `rimflow close` refuses.
