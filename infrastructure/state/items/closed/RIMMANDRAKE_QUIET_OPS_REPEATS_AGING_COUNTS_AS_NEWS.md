# RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS

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

One ticket, two steps, step 1 first. Card picks: "Fix the news bug" (option c) and "Program answers 5 repeat alarms" (option f), analysis sections 3, 4 (items 1 and 2) and 5.

Step 1 (c). src/RimMandrake/rimflow/incident.py `reading_moved` / `revisit_news` (lines 268-316 at ba23c55414): `clock_unit_s` treats a metric as a clock only when its name ends `_min`, `_h` or `_s`, so `plan.days_since_advance`, which ages 1/24 every hour, reads as news and launches a revisit each hour. Grade such a counter by its rate (lesson 20261119T033457Z-CONDUCTOR says so), and grade a flapping count (`wrapup.debris_standing`) by a band, not by any change. Measured: 11 of 42 incident launches were set off by plan or wrapup readings moving; news metrics named: wrapup.debris_standing 8, plan.days_since_advance 6, plan.list_age_h 5.

Step 2 (f). The five repeat no-fix alarms become program routes in src/RimMandrake/rimflow/alarm_routes.json, each with a runbook line. The program writes the same ack and note the LLM wrote, and launches an LLM run only when a stated reading leaves its band (for example unclaimed minutes over N, or runway falling rather than rising). The five (analysis section 3): STEVE_INCIDENT_UNCLAIMED (steve.incident_unclaimed_min), RUNWAY_LOW lukas (accounts.lukas.runway), wrapup.debris_standing, maturation idle (maturation.idle_owed_max_min), scratch dirt (disk.scratch_dirty_end). The builder pins the exact alarm kinds from ops_watch_rules.json and alarms_log.jsonl before writing routes; today all five resolve to `route: role` (steve.*, accounts.*, wrapup.*, maturation.*, disk.*).

Baseline to read first: RIMMANDRAKE_REPAIR_INCIDENT_SELFTEST_TWO_REDS_ON_MAIN says selftest_incident.py was red on main on 2026-11-15 (2 fails). Run it before changing incident.py.
Gates: RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED is held until this item lands (the clerk contains step 1).

## verify

Acceptance test, step 1 (watched it FAIL on main ba23c55414: `days_since_advance aged 1h moved= True ... FAIL 2 cases`; a correct result prints `PASS 2 cases`):

    cd /home/mandrake/rm/bench/src/RimMandrake/rimflow && python3 -c "import incident as I;a=[False,'warn',2.0,True,0];b=[False,'warn',2.0+1/24,True,0];r1=I.reading_moved('plan.days_since_advance',a,b,3600,0);r2=I.reading_moved('plan.list_age_h',[False,'warn',5.0,True,0],[False,'warn',6.0,True,0],3600,0);print('days_since_advance aged 1h moved=',r1,'| list_age_h aged 1h moved=',r2);print('PASS' if (r1 is False and r2 is False) else 'FAIL','2 cases')"

The builder's selftest adds the band cases: wrapup.debris_standing flapping inside its band is not news; a step out of the band is news; a real jump in days_since_advance (a reset to 0) is news.

Acceptance test, step 2 (watched it FAIL on main: `FAIL 0 of 5 program routes with a runbook`; a correct result prints `PASS 5 of 5`). The field name `runbook` is this draft's; if the builder names it otherwise the check changes with it, still five kinds:

    cd /home/mandrake/rm/bench/src/RimMandrake/rimflow && python3 -c "import incident as I;t=I.load_table();ks=['steve.incident_unclaimed_min','accounts.lukas.runway','wrapup.debris_standing','maturation.idle_owed_max_min','disk.scratch_dirty_end'];ok=sum((lambda r:r.get('route')=='program' and bool(r.get('runbook')))(I.route_of(t,k) or {}) for k in ks);print('PASS' if ok==5 else 'FAIL',ok,'of 5 program routes with a runbook')"

Plus every selftest that reads incident.py or alarm_routes.json, by name (selftest_incident.py and its siblings).
Live (analysis section 5, c and f): over the next day of launches, no revisit whose only news is a reading that aged; over 2 days, none of the five alarms launches an LLM run while its reading stays in band.

## criteria

- Both offline checks pass; the band selftest passes; the incident selftests are no worse than their measured baseline.
- alarm_routes.json is an Operations alarm file: the close needs `--live` (e.g. `--live "role=Operations max_age=2d"` or the metronome unit with its reading).

## Close note

The card stamps one owed line on every item it decided: "needs a line a program can check" (from the incident-clerk option). It is RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED's work. A close of any other item names it, e.g. `--why "a line a program can check: filed RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED"`, or `rimflow close` refuses.
