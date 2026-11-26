# RIMMANDRAKE_SLIM_OPERATIONS_START_PACKAGE_HALF_IS_UNRELATED

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

Goal: an Operations role run starts with only what Operations needs, the start package is stable from run to run so it can be cached, and the run is not told it is the Conductor. Card picks: "Slim the start package" (options b + h of the analysis, section 5) and "Trim waste inside a run" (option g). Measured basis, analysis section 2: the start prefix is 56% of Operations spend; median 58,234 tokens, about 27k of it unrelated to Operations [guess ~4 chars/token]; a per-run git-status block and "OWED n" line sit before the stable blocks, so no run reuses another's cache.

1. (b) Add `--exclude-dynamic-system-prompt-sections` and `--disable-slash-commands` to the Operations `launch_args` in src/RimMandrake/rimflow/dispatcher_schedule.json (both are already in role_launch.LAUNCH_ARGS_OK, unused). Its `_launch_args_why` says "Skills stay (used)": that is our own rule from OPS_ROLE_SHRINK_RUN_COST (3 Skill uses in 60 transcripts), and his card pick now removes the skill list; rewrite the why with the card as its source.
2. (b) The seat hooks skip a dispatcher role session (role_launch sets RM_ROLE_UNIT on every role run): project .claude/settings.json SessionStart set_session_title.py; UserPromptSubmit set_session_title.py, bench_mode.py, conductor_goodbye.py; and whichever hook writes the per-run "OWED n" line and injects the CONDUCTOR identity file.
3. (b) Role runs do not load the user CLAUDE.md or MEMORY.md. The analysis lists `--setting-sources` as untested ("Could not measure"): measure it with one probe launch before relying on it. Stable blocks go before anything that varies.
4. (h) Role runs are not told they are the Conductor: no CONDUCTOR identity injection, no "CONDUCTOR" session title.
5. (g) Alarm and incident runs get only their part of roles/operations.md inline (it was read 165 times, 3.9% of spend [measured]); cap Bash output in the brief; ban whole-tree greps over /mnt/d/ClaudeWork/rimmandrake (6 of 64 Sonnet alarm runs timed out on one and lost their summary [measured]).

Scope: Operations launches now. The card says the same change can later go to every role; that is a later item, not this one.
Related, not twins: OPS_ROLE_SHRINK_RUN_COST (the earlier --strict-mcp-config cut), RIMMANDRAKE_DIAGNOSE_OPS_RUNS_OVER_BUDGET_FOUR_OF_ELEVEN (over-long runs).
Gates: RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT waits on this item's live measurement.

## verify

Acceptance test, offline part (watched it FAIL on main ba23c55414: `FAIL 1 of 3 launch flags`; a correct result prints `PASS 3 of 3 launch flags`):

    cd /home/mandrake/rm/bench && python3 -c "import json;op=[r for r in json.load(open('src/RimMandrake/rimflow/dispatcher_schedule.json'))['roles'] if r.get('role')=='Operations' or r.get('name')=='Operations'][0];need=['--exclude-dynamic-system-prompt-sections','--disable-slash-commands','--strict-mcp-config'];ok=sum(f in op.get('launch_args',[]) for f in need);print('PASS' if ok==3 else 'FAIL',ok,'of 3 launch flags')"

Plus the builder's selftest, written with the code: each seat hook named in spec step 2, run with RM_ROLE_UNIT set and a fake session payload, prints no context and no CONDUCTOR identity text, and still prints it without RM_ROLE_UNIT (expected: every hook named, both ways; the builder states the count). Not yet run: it does not exist on main.

Live pass line (the analysis's "First experiment", section 6), over the next >=10 alarm runs and >=5 incident runs, read from the dispatcher records:
- median turn-1 cache_creation <= 28k on Sonnet (from 46,321) and <= 70k on Opus (from 92,323);
- median run weight <= 65k alarm (from 83,864) and <= 190k incident (from 240,427);
- the class-D (note-only) share and the broad-grep-timeout count no worse than baseline (41/64 and 6/64).
- Fail: either median above its line, or a run misses a rule it needed (read 5 transcripts).

## criteria

- C1 L0: Offline check above PASS 3 of 3; the hook selftest passes; every selftest that reads role_launch.py, dispatcher_schedule.json or the hooks is run after the change.
- C2 L3: The live pass line (an evaluation of the dispatcher records and 5 transcripts, not a bridge act). The builder lands the code and marks it implemented. The close waits for the live pass line: the Conductor reads the dispatcher records after the run counts above and closes with `--live "role=Operations max_age=2d"`, citing the measurement.

## Close note

The card stamps one owed line on every item it decided: "needs a line a program can check" (from the incident-clerk option). It is RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED's work. A close of any other item names it, e.g. `--why "a line a program can check: filed RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED"`, or `rimflow close` refuses.
