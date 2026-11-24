# RIMMANDRAKE_LENGTHEN_WAITS_UNDER_ONE_HOUR_CACHE_DIES_AFTER

One wait of up to 55 minutes replaces many waits of ten minutes, and the wait checks that its job lives.

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
| 7 | **Waits.** One wait of up to 55 minutes replaces many waits of ten minutes. A wait over 59 minutes rebuilt the whole cache in 17 of 18 cases `[measured]`. | 8M `[guess ~40%]` | small | A hung job looks like a long job. The wait must check that it lives. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 7 | One long wait in place of many | 43.0M wait turns (2,260); 7.9M are direct repeats (501) | ~12M ~60% | small |

The paragraph of the analysis:

> 7. **Long waits.** A `claude -p` run ends with its turn, so a wait blocks in a call with a 10-minute limit. Raising the
> limit (the `BASH_MAX_TIMEOUT_MS` setting; not set in `settings.json` or `claude_bounded.sh`
> `[measured]`) makes one turn serve a longer wait. It must stay under 59 minutes: of 18 gaps over 59 minutes in detached runs, 17
> rebuilt the whole prompt cache, about 895k each, and twelve 10-minute waits cost about 290k `[measured, scan2.pkl]`. So
> the saving is about 8M `[guess ~40%]`, not 12M. The effect of this setting in a detached run is untested: try it on
> one run first. Risk: a hang that a 10-minute call would have caught. `waitfor.py` must carry its own timeout and
> liveness check.

What else the census printed `[measured]`:

- Wait turns: 2,260, 43.0M (118 per 100 runs); 501 of them, 7.9M, repeat the wait turn before (list items 3.2M, mod fixes 1.5M,
  driver 1.2M) (`p3.py`). A wider rule gives 2,375 turns, 43.2M: list items 15.9M, driver 6.9M, mod fixes 6.6M, Conductor
  window 3.8M, text rewrites 2.6M (`pure.py`).
- `waitfor.py` is named in 272 calls. It has its own timeout (default 30 min, at most 24 h), and it watches a process,
  a job, a file, a line or a port. It has no check that a live process makes progress: a hung process looks like a long one.
- `BASH_MAX_TIMEOUT_MS` is in no settings file and not in `claude_bounded.sh`. The effect in a detached run is **untested**.

**A correction that this filing measured.** The one page first said "one wait of two hours". That would cost more than it saves, so the one page and the analysis
were corrected on 2026-11-23.
Over the main-chain turns of the week's detached runs, grouped by the gap since the turn before (`scan2.pkl`; a rebuild is a
turn that wrote more cache than it read, and over 20k tokens):

| gap before the turn | turns | turns that rebuilt the cache | average cost of a turn | average cost of a rebuilt turn |
|---|---|---|---|---|
| under 1 min | 44,714 | 0 | 21.7k | - |
| 1 to 5 min | 4,644 | 3 | 27.5k | 519k |
| 5 to 11 min | 1,056 | 4 | 24.4k | 534k |
| 11 to 59 min | 48 | 6 | 102.6k | 547k |
| over 59 min | 18 | 17 | 848.4k | 895k |

`[measured]` A wait over 59 minutes rebuilt the whole cache in 17 of 18 cases, about 895k each; twelve waits of ten minutes
cost about 290k (12 at 24k). So a wait must end before the cache does. The 11 to 59 minute row has 48 turns only, and 6 of
them rebuilt: if those 6 are resumes or fleet stops is UNMEASURED. The saving of this item with a 55 minute bound is
about 8M `[guess ~40%]`, not the 12M that the analysis first gave.

From `In-game driver (28 sessions, 114.1M)`:

| job | in → out | class | the program, and does it exist | load | risk |
|---|---|---|---|---|---|
| Wait for scenes | runner log → finished | M | `waitfor.py` exists; each wait is capped by the 10-minute call limit | 6.9M | A hung game looks like a long scene |

From `Offline build (33 sessions, 32.8M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Regenerate the test table and wait for it | M | `make_test_table.py` exists per mod | part of 43.0M waits | Full regeneration is long; the wait is the cost |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Waits | 1,649 | 27.6M | 1.6% |

From `3. Where the week went`:

| kind | found? | where |
|---|---|---|
| Poll a job | yes | waits (43M) |

## spec

### What it must do

- **First act, before any code: test the setting.** Launch one detached run whose brief does one thing: a Bash call with
  `BASH_MAX_TIMEOUT_MS=3300000` in its unit and a `timeout` of 2,700,000 ms, that sleeps 25 minutes and prints a line; then
  one short turn. Read from its transcript: how long the call lasted, if the harness cut it, and if the turn after it read
  the cache (`cache_read_input_tokens`) or wrote it again (`cache_creation_input_tokens`). Then one more of 50 minutes. Write
  `design/specs/2026-11-23-long-waits/experiment.json`.
- `detached_helper.launch_argv` then sets the variable in the unit, at a value that the experiment proved, at most 59 minutes.
- `src/RimMandrake/Utils/waitalive.py` runs a command, or attaches to one that it started earlier, and waits for its end with
  its own bound (default 55 min) and its own sign of life: growth of the output, of a progress file, or of the CPU time of
  its process tree.
- It ends with one verdict line and a different exit for: finished well, finished badly (with the code), hung (with the pid),
  still running at the bound, died, could not look. A job still running at the bound keeps running; the next call attaches.
- The started job holds no pipe of the caller, or the call never returns (found while the test was written).
- The brief's line about waits names the command.

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
- The risk (one page): *"A hung job looks like a long job. The wait must check that it lives."* The guard: the sign of life above,
  and HUNG as its own exit with the pid. It kills nothing: to stop the job is the agent's decision.
- It must not let a wait outlive the prompt cache (59 minutes). The number, its danger and the table above go on the page
  under LIMITS.
- It must not turn "still running" or "died" into "finished", and must not lose the job's own exit code.
- It must not replace a wait that the harness can notify (a background command that re-invokes a window): it is for
  `claude -p` runs, whose turn ends the run.
- It must not make the launch of a run fail when the variable is not known to a newer Claude Code.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank7_long_waits_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/14`, exit 1. Expected on a correct build:
`PASS 14/14`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: ended well, failed, hung and silent, slow but alive, silent but busy, past the bound, attached, never started,
killed, no command, and the experiment's record.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-long-waits/boundary.md`. Selftest: `src/RimMandrake/Utils/selftest_waitalive.py`. Planted
faults that the tests must catch:

- a silent idle job is called alive; a busy silent job is called hung;
- exit 7 reads as 0; a killed job reads as finished; an unknown job reads as finished;
- the bound is over 59 minutes; the job is killed at the bound;
- the experiment file says that the call was cut, and the setting is used anyway.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 p3.py
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

- Must fall: `wait` (2,260 turns, 43.0M; 118 per 100 runs) and `wait_repeat` (501 turns, 7.9M; 26 per 100 runs). Guess: 12M
  less a week `[guess ~60%]` in the analysis; about 8M with the 55 minute bound `[guess ~40%]`.
- Must not get worse: `cache_rebuilt_after_gap` (turns after a gap of 11 minutes or more that rebuilt the cache: 23 in the
  baseline, 6 and 17, about 18.5M `[measured]`), and **hung jobs found late** (the time between the last sign of life and
  the report). The second has no baseline: UNMEASURED. `waitalive.py` logs each HUNG verdict with its silent time, so the
  week after has a number.

## How it keeps improving

- `wait_repeat`: agents that still poll. `sleep` loops in commands name the waits that the tool does not cover.
- The HUNG and STILL RUNNING lines of the week: many STILL RUNNING verdicts mean that the bound is too short for a job that
  should be its own unit.
- After each Claude Code update: one reading of the experiment again (a setting can lose its effect in silence).

## Size and order

Rank 7. Size: small. It enters the build pipeline now: its outcome check fails, it waits on nothing, so the List Pipeline's
launch step starts it. **Its first act is to test the setting** (below). If the
setting does not work in a detached run, the builder writes the reading on the item, puts a dated wait on it for the
Conductor, and builds nothing more.

## criteria

- The experiment file exists, from a real detached run, with its transcript path.
- The acceptance test prints PASS 14/14, or the item waits on the Conductor with the reading that the setting does not work.
- The page holds the limit, its danger and the table above.
