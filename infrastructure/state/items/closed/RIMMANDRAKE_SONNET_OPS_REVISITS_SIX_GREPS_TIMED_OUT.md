# RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT

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

Card pick: "Sonnet for follow-ups only" (typed by him in the card). Revisit runs move to Sonnet only after the slim start package is measured; first looks and the economy pass stay Opus. "Sonnet for every run" was NOT picked.

His words with it, verbatim: "If we escalate to (4) then we would likely give Sonnet Escalation: recognize something is fishy, so call out Opus to continue." ((4) = Sonnet for every run.)
The Conductor's reading, as its own act and not his words: any Operations run on Sonnet gets an escalation route; it says "this is fishy" and an Opus run continues. That route is built here.

1. In src/RimMandrake/rimflow/dispatcher_schedule.json the Operations `model_by_mode` (today `{"alarm": "sonnet"}`) sends revisit runs to Sonnet; incident first looks and the economy pass stay Opus. The builder finds the mode name the dispatcher gives a revisit launch.
2. Escalation route: a Sonnet run that finds something fishy records it in one stated, machine-readable way, and the dispatcher launches one Opus run that continues from the Sonnet run's notes. No loop: an Opus continuation does not escalate again.
3. Known Sonnet failure to guard against (analysis section 3): 6 of 64 Sonnet alarm runs, 0 of 36 Opus runs, started a broad background grep that hit its time limit and lost the summary.

Held: until RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED's live measurement passes (rimflow block, --on that item, until done; that item closes only on its measurement).

## verify

Acceptance test: a selftest written with the code: the dispatcher picks Sonnet for a revisit, Opus for an incident first look and for the economy pass (3); a Sonnet run's escalation record launches exactly one Opus continuation carrying its notes (1); an Opus continuation's escalation record launches nothing more (1). Expected `5 of 5`. Today's probe (watched it FAIL on main ba23c55414: `FAIL {'alarm': 'sonnet'}`; a correct result prints PASS):

    cd /home/mandrake/rm/bench && python3 -c "import json;op=[r for r in json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json'))['roles'] if r.get('role')=='Operations' or r.get('name')=='Operations'][0];m=op.get('model_by_mode',{});ok=any('revisit' in k and v=='sonnet' for k,v in m.items());print('PASS' if ok else 'FAIL',m)"

Live (analysis section 5, combinations): over the next >=5 Sonnet revisit runs, the broad-grep-timeout rate is no worse than 6/64 and every escalation is followed by an Opus run.

## criteria

- Selftest 5 of 5; every dispatcher and role_launch selftest run after the change.
- Touches dispatcher_schedule.json: the close needs `--live "role=Operations max_age=2d"`.

## Close note

The card stamps one owed line on every item it decided: "needs a line a program can check" (from the incident-clerk option). It is RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED's work. A close of any other item names it, e.g. `--why "a line a program can check: filed RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED"`, or `rimflow close` refuses.
