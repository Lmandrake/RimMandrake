# RIMMANDRAKE_BUILD_ONE_TEST_CALL_PARENT_FIX_AND_FAULT

One call runs a test on the old code, the new code and a planted fault.

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
| 4 | **Tests.** One call runs a test on the old code, the new code and a planted fault. | 20M `[guess ~50%]` | medium | It can read the wrong build. It must print which build it read. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 4 | One test call: parent, fix, planted fault | 123.3M test turns (6,085); 37.8M run one test and write nothing; 19.5M are red/green | ~20M ~50% | medium |

The paragraph of the analysis:

> 4. **One test call.** A command runs the named test on the parent tree and the working tree, plants the given fault, and
> prints the failing lines. `red-seen` does the planted half. The agent chooses the test and the fault. Risk: a test
> that needs the built DLL reads the wrong tree; the command must print which build it read.

What else the census printed `[measured]`:

- Turns that run a test: 6,085, 123.3M (`p5.py`); 2,184 of them, 37.8M, run one test and write nothing.
- Red/green and planted-fault turns: 864, 19.5M (list items 9.0M, mod fixes 2.6M, driver 1.8M, fixer 1.4M) (`pure.py`).
- `maturation.py red-seen` is named in 418 calls (`p3.py`). It applies the fault, runs the test, wants a non-zero exit, and
  reverses the fault (`judge_certificate.red_seen`). It reads a test of a mod's test table only, and it does not run the
  parent. Parent-against-fix is done by hand with `git show` or a worktree.
- Offline tests are the largest act of the week: 10,407 turns, 181.2M, 10.5%.

From `In-game fixer, and mod fixes and traces (172 sessions, 256M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Before and after test of the fix | M | `red-seen` exists for planted faults; parent-against-fix is done by hand with `git show` or a worktree | 19.5M red/green turns | A test that needs a build, or a file that the parent lacks |

From `In-game driver (28 sessions, 114.1M)`:

| job | in → out | class | the program, and does it exist | load | risk |
|---|---|---|---|---|---|
| Plant a fault and show red, then green | fault patch, test → two readings | X | `maturation.py red-seen` runs it; the agent writes the patch | 14.0M (all roles) | An equivalent mutant reads green and means nothing |

From `Offline build (33 sessions, 32.8M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Check the deciders are red when they must be | X | `red-seen` exists | 14.0M (all roles) | Equivalent mutants |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Run offline tests | 10,407 | 181.2M | 10.5% |

From `Text rewrites (195 sessions, 204.1M) and art work (15, 26.8M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| "Lose nothing" check | M | exists for rule files; per-file variants each time | 11.2M tests | — |

## spec

### What it must do

- One call, `src/RimMandrake/Utils/redgreen.py`, runs one named test on the parent commit and on the working tree, plants each
  given fault on the working tree, runs the test again, and reverses the fault.
- It prints for each leg: red, green or could not look; the exit; the failing lines; the tree that was read; the hash of
  each built file that the test reads.
- It gives one answer: RED_THEN_GREEN, GREEN_ON_PARENT, RED_ON_WORK, GREEN_ON_FAULT or COULD_NOT_LOOK.
- A new test file is laid over the parent on request.
- `red-seen` stays the record of a mod's deciding test; this call uses the same planting code, not a second copy of it.

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
- The risk (one page): *"It can read the wrong build. It must print which build it read."* The guard: each leg prints its tree
  and the hash of each built file it was told of; an absent built file makes the answer COULD_NOT_LOOK. The parent leg runs in
  a clean copy, so a test that needs a build that the copy lacks is could not look, never red.
- It must not choose the test or the fault, and must not write a fault.
- It must not read a crash, an import error, a hang or a missing file as red: only exit 1 is red.
- It must not change the caller's tree or index, uncommitted edits included, also after a kill.
- A live test is not for this call (`red-seen` refuses a fault that the game never loads; keep that refusal).

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank4_one_test_call_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/15`, exit 1. Expected on a correct build:
`PASS 15/15`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: missing test, crash, hung test, stale fault (does not apply), equivalent fault, absent build, uncommitted edits.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-one-test-call/boundary.md`. Selftest: `src/RimMandrake/Utils/selftest_redgreen.py`.
Planted faults that the tests must catch:

- exit 2 or a timeout counts as red; an import error on the parent counts as red;
- the parent leg reads the working tree (both legs the same); the cached `.pyc` of one leg is read by another;
- the fault stays in the tree after a hang; the index changes;
- a fault that does not apply reads green; a green fault leg still gives RED_THEN_GREEN;
- a leg prints no build.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 p5.py; python3 pure.py
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

- Must fall: `one_test` (2,184 turns, 37.8M; 114 per 100 runs) and `red_green` (864 turns, 19.5M; 45 per 100 runs). Guess:
  about 20M less a week `[guess ~50%]`, of a pool of 123.3M test turns.
- Must not get worse: **fixes whose test was never red on the parent**. Baseline UNMEASURED: before the change lands, the
  builder samples 20 fixes of the baseline week and counts those with a red reading on the record.

## How it keeps improving

- The share of `redgreen.py` answers that are COULD_NOT_LOOK, by cause: a cause that returns names a missing feature (a
  build, a fixture).
- `git show <sha>:<file>` and worktree commands in test turns (`red_green` in `window.py`): agents still do it by hand.

## Size and order

Rank 4. Size: medium. **This item waits.** Its reason: waits until the small items are built and their 7-day measurement is
read. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads the measurements and decides which waiting item
goes next. The small items are ranks 3, 5, 6, 7 and 10. A builder does not start this item before that decision.

## criteria

- The acceptance test prints PASS 15/15.
- `red-seen` and this call share the planting code.
- One real fix was shown with the call, and its output is on the item.
