# RIMMANDRAKE_TIE_LIFE_SIGN_TO_PROCESS_484_HAND_NOTES

A run's sign of life and its lease come from the running process, not from the agent's hand.

Filed by `RIMMANDRAKE_TICKET_TEN_AGENT_WORK_TO_CODE_CHANGES_SMALL_ONES_FIRST`. The owner, 2026-11-23, evening PST: *"let's please
ticket each of these as work items fully including what metrics that would answer to (how to know they're written
well and improving), how to measure that they helped vs. the past, what they must do, what they must not do, etc. Then
let's accept the small ones into the build pipeline, while postponing the medium and large items until we learn from
the small ones."*

## Finding

The finding is from the agent-work census of 2026-11-23 (item
`RIMMANDRAKE_FIND_AGENT_WORK_THAT_PYTHON_CAN_DO_TOKEN_FREE`). The week is the 7 days to 2026-11-23, 7:56 PM PST. M is
million weighted tokens (`weighted_v2`: 1 is one uncached Opus 5.5 input token). The whole analysis:
`design/specs/2026-11-23-agent-work-to-code/analysis.md`; the one page: `one_page.md` beside it; the scripts: `census/`
beside it.

- The week cost 1,718.7M in 1,908 transcripts with a priced turn (1,935 parsed) `[measured]`; 731 detached run records,
  1,373.8M `[measured]`. The records and the transcripts are 3% and 5% apart `[measured]`.
- Paperwork turns (land, ledger, stage tools, state reads, game lock, waits, build and deploy) cost 398.5M, 23% of the
  week `[measured by the act rules]`. The ten changes together save about 120M a week, 7% `[guess ~50%]`. The ten pools
  overlap, so their savings do not add up.
- An act rule gives a turn to one act (the first rule that matches), so each pool has an error; an act that shares a
  turn with other work is under-counted `[measured: publish is in 4,022 commands, only 2,312 show PUBLISHED]`. A run is
  put in a role by its item name; about 5% may be in the wrong row `[guess]`.
- Not seen: Codex and GPT tokens, SteveDesktop and the Macs: UNMEASURED. A real saving is UNMEASURED until this is built.
- What a pasted text costs: a packet of 3,000 tokens that stays for 60 turns costs about 9,000 weighted tokens plus a
  first load of about 6,000; one turn that it removes costs 15,000 to 30,000 (the analysis's arithmetic).

The row of the one page:

| rank | what moves to code | saved in a week | build | risk in one line |
|---|---|---|---|---|
| 10 | **Sign of life.** The lease and the 20-minute note come from the running process. | 8M `[guess ~55%]` | small | A hung run keeps its lease. Tie the lease to the process. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 10 | Lease and progress note by program | 14.3M progress notes (484) + 7.5M lease renewals (202, often mixed) | ~8M ~55% | small |

The paragraph of the analysis:

> 10. **Lease and progress.** The lease lives with the process (the game lock does this). The progress note every 20
> minutes is written from the run's own last message and commits. Risk: the theory and the reading in a progress note
> are judgement; keep the note at the end of an experiment, and let the program do only the 20-minute "alive" line.

What else the census printed `[measured]` (`p6.py`, `pure.py`):

- Progress note turns (a `note` with PROGRESS or STATE): 484, 14.3M, 29k each (25 per 100 runs).
- `lease.renew` turns: 202, 7.5M, 37k each, often mixed with other work; 21 turns, 0.4M, renew the lease and do nothing
  else. `modledger append` turns in all: 370, 10.9M.
- Where the asks come from `[measured]`: `detached_helper.FOOTER` asks for a state note "at least every 20 minutes" and for a
  PROGRESS note after each experiment; `maturation_dispatch.renew_line` tells a mod's holder to renew its lease every
  two thirds of `lease_idle_minutes`, because a lapsed lease refuses the closing checkpoint (GimmeSomeSlack blind cycle 5,
  2026-11-16 1:03 AM PST).
- The game lock already lives with its process: when the holder ends, the game is free at once.

From `In-game driver (28 sessions, 114.1M)`:

| job | in → out | class | the program, and does it exist | load | risk |
|---|---|---|---|---|---|
| Lease renew, ledger notes | clock → events | M | Agents run `modledger.py append … lease.renew` | 7.5M (all roles, often with other work) | A hung run would keep its lease; tie it to process life, as the game lock does |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Ledger writes | 4,357 | 81.6M | 4.7% |

## spec

### What it must do

- A timer program, `src/RimMandrake/rimflow/run_alive.py`, looks at each live detached run: is the unit up, is the process there,
  did its transcript grow, does it run a command now.
- A run that lives has its mod lease renewed by the program, with the writer and the token of that run.
- A run that is gone, or hung (silent past the longest allowed call with no command running), is not renewed: its lease
  lapses, and the status line says which of the two.
- The 20-minute "alive" line comes from the run's own last message and its commits. It is kept in one file beside the run
  record (`<unit>.alive.json`) and shown by `detached_helper.py status`. The ledger gets it once, at a stop, through `finish`,
  so that a continuation has it.
- The footer no longer asks for a 20-minute note. It keeps the PROGRESS note after an experiment, and the closing words.
- `renew_line` goes out of the brief when the timer is live, not before: a run launched before the timer lives keeps it.

## What it must not do

- It must not take a judgement from an agent. Finding a cause, designing a fix, choosing words, judging a picture,
  choosing a planted fault, naming a hole, classing a failure (MOD, SITE, HARNESS, ENVIRONMENT, COULD NOT LOOK), and
  deciding if a ticket is worth doing stay with agents. Talk with the owner and his five acts stay with him.
- It must not hide a failure. A failed step reads failed, with its cause, where the agent looks first.
- It must keep "could not look", "failed", "zero" and "empty" apart in every return value, line and exit code. A step
  that gave no reading is never an answer.
- It must not tell a launched agent its spend: no token figure, budget, cap or price in a brief, a packet, a note that an
  agent reads, or a tool's output. Text that people wrote goes through `spend_talk.strip`.
- It must not refuse an act for a fault of form that it can repair itself.
- The risk (one page): *"A hung run keeps its lease. Tie the lease to the process."* The guard: process, unit, transcript and child
  command are read; hung is its own word, and a hung run's lease lapses.
- It must not write a theory, a reading or a next act: the PROGRESS note is judgement and stays with the agent.
- A beat that could not read a fact is blind: it renews nothing, lapses nothing and says so. A blind beat is never "dead".
- It must not renew a lease with a stale token, or for a run whose lease another holder fenced: the refusal is kept as
  refused, never as renewed.
- It must not raise an alarm, kill a run, or write a ledger note each beat.
- It must not count a long wait (its command runs) as hung.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank10_sign_of_life_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/20`, exit 1. Expected on a correct build:
`PASS 20/20`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: alive, not due, dead, hung, long wait, each unreadable fact, empty message, refused renewal, no lease.

The live part (the timer beats on real runs): the `--live` promise at close, `unit=rm-run-alive.timer reading=<its reading file>
max_age=1h`.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-run-alive/boundary.md`. Selftest: `src/RimMandrake/rimflow/selftest_run_alive.py`. The existing
tests that want `lease.renew` in a holder's brief (`selftest_dispatch_pilot_holder.py`, `selftest_pilot_stage_runs.py`) change
with it. Planted faults that the tests must catch:

- a hung run is renewed; a dead run is renewed; a long wait is called hung;
- an unreadable transcript counts as alive or as dead;
- a refused renewal reads renewed; a run with no lease calls append;
- the alive line holds a theory, or the spend of the run's own words;
- the footer loses the PROGRESS line.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 p6.py
```

The kept data is `scan3.pkl` (and `scan2.pkl`, `rows.pkl`) in that folder, made once by `runs.py`, `scan.py`, `det.py`,
`scan3.py`. Never write over that folder. The scripts themselves are in the repo (`census/`).

**The census must change before the comparison is possible** `[measured]`: the scripts have no upper time bound, their
output folder is fixed (a second run destroys the baseline), and `scan.py`, `scan3.py` and `outc.py` import from a clone
that is gone (`outc.py` fails today with ModuleNotFoundError). That change, `census/window.py`, is the second part of
`RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES`. If it has not landed when this item is measured, build
it here first, to the contract in `design/specs/2026-11-23-agent-work-to-code/acceptance/census_window_accept.py`.

The same reading again, 7 days after the change is live (put the time in the close of this item):

```
python3 design/specs/2026-11-23-agent-work-to-code/census/window.py --end <live time + 7 days, ISO> --days 7 \
    --out /mnt/d/ClaudeWork/rimmandrake/scratch/a2c_<date>
```

Read `rates.json`. A week differs from another week in size, so compare turns **per 100 runs** and weighted tokens **per
100 runs**, never the bare weekly sum. The baseline has 1,908 runs. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads these numbers.

- Must fall: `progress_note` (484 turns, 14.3M; 25 per 100 runs) and `lease_renew` (202 turns, 7.5M; 11 per 100 runs). Guess:
  about 8M less a week, of 21.8M `[guess ~55%]`.
- Must not get worse: **leases that lapsed under a live run** (appends refused as stale or lapsed, read from the mod ledgers) and
  **stopped runs that were carried on with no state** (continuations whose item has no ALIVE, PROGRESS or state note from the
  run before). Baselines UNMEASURED: the builder counts both over the baseline week first. PROGRESS notes after an experiment
  may fall no more than the 20-minute ones: read ten runs to tell them apart.

## How it keeps improving

- `lease_renew` turns by agents after the change: a brief that still asks for them.
- Blind beats by cause in the timer's reading: a fact that moved.
- The reading's age (`rm-deadman` rechecks the promise for good).

## Size and order

Rank 10. Size: small. It enters the build pipeline now: its outcome check fails, it waits on nothing, so the List Pipeline's
launch step starts it. It is operational: it closes only with `--live`.

## criteria

- The acceptance test prints PASS 20/20.
- The timer runs, its reading is fresh, and the close carries `--live`.
- A test run that was killed lost its lease, and a run in a long wait kept it (both readings on the item).
