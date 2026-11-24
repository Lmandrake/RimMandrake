# RIMMANDRAKE_BUILD_ONE_LANDING_COMMAND_215_FORM_REFUSALS

One command lands work: commit, publish, retry, note, close.

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
| 1 | **Landing.** One command commits, publishes, retries, notes and closes. | 35M `[guess ~60%]` | medium | It makes closing easy. Keep the outcome check in its path. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 1 | One landing-and-closing command | 74.6M pure landing turns (4,408 turns, 907 runs, median 4 a run) + 34.4M refused-publish repairs (420) | ~35M ~60% | medium |

The paragraph of the analysis:

> 1. **Landing and closing.** A `finish` command takes the paths, the subject, the evidence and the item. It commits,
> publishes, retries a race, writes the note, closes the item and prints one line. Form refusals (pathspec, usage,
> "nothing to publish": 215 cases, 14.7M) are repaired inside it. It stops for a red check (77 cases) and a content
> conflict (54). `./publish` and `cli.py close` exist. Risk: an agent may close work that is not finished, because
> the command makes it easy. Keep the close check (`list_effect`, `--live`) in the path.

What else the census printed about this pool (`pure2.py`, `p5.py`, `pure.py`) `[measured]`:

- 4,408 turns that only land work or write the ledger, 74.6M, in 907 runs, median 4 a run. By role: list items 32.3M,
  Conductor window 9.5M, mod fixes 7.3M, in-game driver 5.5M, text rewrites 5.0M, Conductor subagents 3.3M, fixer at
  in_game 3.2M.
- By verb: publish alone 1,901 turns, 30.0M; note 499, 9.2M; file 338, 5.5M; close 311, 4.7M; note and publish 160, 3.5M;
  sync or commit 213, 3.2M; claim 30, 3.1M; close and verify 64, 1.1M; close and note 55, 1.1M; close and publish 70, 0.9M.
- 1,020 of these turns follow another one directly (14.6M).
- 420 refused publishes cost 34.4M from the refusal to the next PUBLISHED line (at most 7 turns counted; 82k each). By
  cause: form (command shape) 215 cases, 14.7M; a check is red 77, 8.0M; replay conflict 54, 6.1M; other 48, 3.9M; race on
  origin 26, 1.8M. The races are few: the form cases are the saving.

From `In-game fixer, and mod fixes and traces (172 sessions, 256M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Publish, note, close | M | section 6, rank 1 | 74.6M (all roles) | — |

From `List Pipeline: Shape, Work, Verify, Launch, View, Audit`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Work: read the item, do it, run its check, land, close | X | the Work brief lists five shell steps; the landing and close are M | part of 77.9M | The need can be wider than the check; the brief says so |

From `Conductor window (136 sessions, 193.7M) and its subagents (169, 102.0M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Record his words and ledger writes | X | his words go in as he typed them | 14.0M ledger, 1.3M open page | — |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Land (publish, commit, sync) | 5,428 | 90.0M | 5.2% |
| Ledger writes | 4,357 | 81.6M | 4.7% |

## spec

### What it must do

- One command, `src/RimMandrake/Utils/finish.py`, takes the item, the paths, the subject and the evidence.
- It commits and publishes the named paths, retries a race on origin itself, and finds the sha when the work is already
  on origin.
- It repairs a form refusal inside itself: a pathspec, a usage fault, "nothing to publish".
- It runs the item's outcome check (`list_effect.py check`) on the landed work, and closes only when the check holds (or
  the item has none, and then it says so). An operational item passes its `--live` promise through.
- It writes the note with the evidence, closes the item on the sha, lands the ledger write, and prints one line: what was
  landed, what was closed, or the one thing that stopped it.
- It stops at once, with the tool's own words, for a red check, a content conflict, or a hook.

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
- The risk (one page): *"It makes closing easy. Keep the outcome check in its path."* The guard: the outcome check stands
  between the landing and the close, with no flag that skips it. A check that fails, hangs or reads unmeasured leaves the
  item open and says which of the three it was.
- It must not weaken the close gate of rimflow (`_close_gate`), pass an owner flag, or choose the evidence text.
- It must not repair a red check, resolve a conflict, stash, reset, force a push or stage a path that was not named.
- It must not file, drop or wait an item, or write `LEFT OPEN:` for the agent: what is left is a judgement.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank1_landing_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/18`, exit 1. Expected on a correct build:
`PASS 18/18`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: landed, empty input, missing path, hung publish, hung check, unmeasured check, failing check, race, endless race,
red check, conflict, hook, refused close, a close written and not landed. Live part (a real push from a real clone): the
builder lands this item's own last change with the command and puts the printed line in the close.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-one-landing-command/boundary.md`. Selftest: `src/RimMandrake/Utils/selftest_finish.py`.
Planted faults its tests must catch:

- the outcome check's failing exit is read as a pass; its hang is read as a pass; its unmeasured exit is read as a fail;
- a red check is retried as a race;
- "exit 0 with no PUBLISHED line" is read as landed;
- a close that rimflow refused, or wrote and did not land, reads closed;
- the sha of another commit is closed on;
- the command publishes a path that was not named.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 pure2.py; python3 p5.py; python3 pure.py
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

- Must fall: `pure_landing` (4,408 turns, 74.6M; 231 turns per 100 runs) and `publish_refused` (420 cases, 34.4M; 22 per
  100 runs). Guess: about 35M less a week, a third of the two pools together `[guess ~60%]`.
- Must not get worse: **wrong closes**, the items that were closed and then reopened (a `verify` fail on a closed sha, a
  broken promise) per 100 closes. Baseline UNMEASURED: the builder counts the reopens of the baseline week from the ledger
  before the change lands, and puts the count here.

## How it keeps improving

- `form (command shape)` refusals in `p5.py`: they should stay near 0. A new kind means that `publish.py` changed and
  `finish.py` did not.
- Agents that still call `./publish` and `cli.py close` apart after the change (`pure_landing` by verb): a role whose brief
  does not name the command.

## Size and order

Rank 1. Size: medium. **This item waits.** Its reason: waits until the small items are built and their 7-day measurement is
read. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads the measurements and decides which waiting item
goes next. The small items are ranks 3, 5, 6, 7 and 10. A builder does not start this item before that decision.

## criteria

- The acceptance test prints PASS 18/18.
- A landing by the command closed this item.
- The reopen baseline is on the item.
