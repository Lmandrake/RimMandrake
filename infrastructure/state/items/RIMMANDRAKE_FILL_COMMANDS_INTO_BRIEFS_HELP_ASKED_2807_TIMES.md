# RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES

The brief of a detached run carries each command of the run, filled in, made from the tool itself.

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
| 3 | **Commands.** The brief carries each command filled in. Agents ask for help text 2,807 times a week `[measured]`. | 20M `[guess ~50%]` | small | The text goes stale. A program makes it from the tool itself. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 3 | Filled commands in the brief | 51.3M `--help` turns (2,807); 23.0M of these on ledger, stage, launch, lesson and publish verbs | ~20M ~50% | small |

The paragraph of the analysis:

> 3. **Filled commands.** The launcher pastes the exact commands of the run (file, note, close, verify, red-seen, lessons),
> filled in, made from `argparse` at launch. `maturation.py brief` already does part. Risk: the text goes stale; make it
> from the parser, never by hand. Watch if agents still ask `--help`.

What else the census printed `[measured]`:

- `--help` turns: 2,807, 51.3M, 18k each (147 turns per 100 runs). By role: list items 16.1M, Conductor window 8.5M, mod
  fixes 5.8M, text rewrites 4.3M, in-game driver 3.9M (`pure.py`).
- 1,136 of them, 23.0M, ask for a ledger, stage, launch, lesson or publish verb (`p6.py`).
- By tool (`p3.py`): `cli.py file` 360 turns, 6.17M; `cli.py` 128, 1.73M; `detached_helper.py launch` 44, 1.67M; `cli.py
  close` 68, 1.55M; `maturation.py red-seen` 67, 1.36M; `run_selftests.py` 94, 1.36M; `gpt_consult.py` 52, 1.18M; `publish`
  66, 1.02M; `cli.py note` 66, 0.90M; `maturation.py` 54, 0.88M; `modset_builder.py` 45, 0.83M; `cli.py verify` 48, 0.75M;
  `code_review_status.py` 57, 0.63M; `lessons.py add` 41, 0.61M; `game_instance.py` 36, 0.59M; `maturation.py unrun` 37,
  0.56M; `testq.py` 31, 0.55M; `modledger.py append` 32, 0.53M; `winbuild.py` 31, 0.52M; `cli.py drop` 18, 0.37M;
  `waitfor.py` 25, 0.33M.
- Beside them: 346 turns, 6.1M, used a wrong flag without asking (`usage:`, `unrecognized arguments`); 2,982 turns, 43.3M,
  read tool source in runs that are not about tools (text rewrites 11.0M, Conductor subagents 7.8M, mod fixes 6.8M, driver
  4.7M).
- The footer of every detached brief (`detached_helper.FOOTER`) already fills four `cli.py` commands by hand. They are
  text in the code, not made from the parser. `maturation.py brief` fills the stage commands of a mod run.

From `3. Where the week went`:

| kind | found? | where |
|---|---|---|
| Re-derive a fact that a tool prints | yes, large | `--help` (51.3M), `show` cut by hand (39.1M), raw ledger reads (15.5M) |

From `Conductor window (136 sessions, 193.7M) and its subagents (169, 102.0M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Launch helpers; write briefs | X | `detached_helper.py launch` exists | 6.3M + 2.0M | — |

From `Offline build (33 sessions, 32.8M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Read which bars are left | M | `maturation.py brief`, `next` exist | UNMEASURED | — |

## spec

### What it must do

- A module, `src/RimMandrake/rimflow/brief_commands.py`, makes one filled line for each command that a detached run uses:
  `cli.py file`, `note`, `wait`, `close`, `verify`; `maturation.py red-seen`; `lessons.py add`; `./publish`. The item and the
  seat are filled in. Every required flag is in the line. A flag whose value the agent chooses has a named blank.
- The lines are made from the tool's own `argparse` parser when the run is launched, so a changed flag shows in the next
  brief with no edit.
- `detached_helper.brief_message` puts the lines in the brief of every detached launch; the hand-written copies of the same
  commands in `FOOTER` go away (a command has one home).
- A tool whose parser cannot be read is named in the text as "could not look: run `<tool> --help`".
- Second part: `census/window.py`, so that the same counts can be made for any week (contract in
  `acceptance/census_window_accept.py`). The rules move from the old scripts; no rule is written new. Run it once over the
  baseline window (`--end 2026-11-23T19:56:44-08:00`) and put its numbers beside 2,807, 1,615, 2,260, 484 and 202 on this
  item. A transcript may have been deleted since, so say how many runs each reading saw.

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
- The risk (one page): *"The text goes stale. A program makes it from the tool itself."* The guard: the lines come from the
  parser at launch, and a test changes the parser and sees the text change. No line is written by hand.
- It must not paste the help text of a tool whole: the text stays below 12,000 characters, because it stays in the context
  for every turn (the danger: the first load of a run is 83k weighted tokens on average `[measured]`, and each character is
  read again each turn).
- It must not fill in a value that is a judgement: the evidence text, the reason, the class, the level, the result.
- It must not name the five acts of the owner or an owner flag as a command to run.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank3_filled_commands_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/15`, exit 1. Expected on a correct build:
`PASS 15/15`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

### Acceptance test of the census window

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/census_window_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/12`, exit 1. Expected on a correct build:
`PASS 12/12`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
This one was not run against a stub. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-brief-commands/boundary.md`. Selftest: `src/RimMandrake/rimflow/selftest_brief_commands.py`.
Planted faults that the tests must catch:

- a line whose flag is not in the parser; a required flag left out; the item or the seat not filled in;
- a verb that is gone from the parser is dropped in silence; a parser that raises gives an empty text;
- the launch path builds its message without the lines;
- a spend word in the text.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 p6.py; python3 p3.py; python3 pure.py
```

The kept data is `scan3.pkl` (and `scan2.pkl`, `rows.pkl`) in that folder, made once by `runs.py`, `scan.py`, `det.py`,
`scan3.py`. Never write over that folder. The scripts themselves are in the repo (`census/`).

**The census must change before the comparison is possible** `[measured]`: the scripts have no upper time bound, their
output folder is fixed (a second run destroys the baseline), and `scan.py`, `scan3.py` and `outc.py` import from a clone
that is gone (`outc.py` fails today with ModuleNotFoundError). That change, `census/window.py`, is the second part of
`this item (the section above)`. If it has not landed when this item is measured, build
it here first, to the contract in `design/specs/2026-11-23-agent-work-to-code/acceptance/census_window_accept.py`.

The same reading again, 7 days after the change is live (put the time in the close of this item):

```
python3 design/specs/2026-11-23-agent-work-to-code/census/window.py --end <live time + 7 days, ISO> --days 7 \
    --out /mnt/d/ClaudeWork/rimmandrake/scratch/a2c_<date>
```

Read `rates.json`. A week differs from another week in size, so compare turns **per 100 runs** and weighted tokens **per
100 runs**, never the bare weekly sum. The baseline has 1,908 runs. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads these numbers.

- Must fall: `help_ledger_verbs` (1,136 turns, 23.0M; 60 per 100 runs) and with it `help` (2,807 turns, 51.3M; 147 per 100
  runs). Guess: about 20M less a week `[guess ~50%]`. A good result is `help_ledger_verbs` under 20 per 100 runs.
- Must not get worse: `wrong_flag` (346 turns, 6.1M; 18 per 100 runs); and the first load of a run (83.0k weighted tokens on
  average), which may rise by no more than the text's own load.

## How it keeps improving

- `help` by tool (`p3.py`): a tool that agents still ask about is missing from the lines, or its line is wrong.
- `wrong_flag`: a rise means that a line and its parser parted.
- The could-not-look lines in the briefs of the week (`*.brief.md` in `D:\ClaudeWork\rimmandrake\dispatcher\detached`): more than 0 names a parser that moved.

## Size and order

Rank 3. Size: small. It enters the build pipeline now: its outcome check fails, it waits on nothing, so the List Pipeline's
launch step starts it. It is the first of the five: its second part makes the measurement of
all five possible. `RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT` edits the same launcher function; whoever lands second
uses `brief_message` as it stands.

## criteria

- The acceptance test prints PASS 15/15, and the census window's prints PASS 12/12.
- The brief of one real detached run launched after the change holds the lines (path of its `.brief.md` on the item).
- The census window's reading of the baseline week is on the item.
