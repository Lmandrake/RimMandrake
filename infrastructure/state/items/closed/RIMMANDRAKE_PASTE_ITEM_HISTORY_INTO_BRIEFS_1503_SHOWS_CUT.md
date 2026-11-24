# RIMMANDRAKE_PASTE_ITEM_HISTORY_INTO_BRIEFS_1503_SHOWS_CUT

The launcher puts the item's history in the brief, with a count of what it left out.

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
| 6 | **Item history.** The launcher puts the item's history in the brief. | 15M `[guess ~50%]` | small | The packet can omit the one decisive note. It must say what it left out. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 6 | Item packet at launch | 41.9M `show` (39.1M cut by hand) + 15.5M raw ledger reads | ~15M ~50% | small |

The paragraph of the analysis:

> 6. **Item packet.** The launcher runs `show`, folds the notes into state, last run, linked items and the last commits,
> and pastes it. `modledger` already builds such a packet for mods. Risk: a packet that omits the one decisive note; it
> must say what it left out and print the command that shows it.

What else the census printed `[measured]` (`p6.py`):

- `cli.py show`: 1,615 turns, 41.9M, 26k each (85 turns per 100 runs). 1,503 of them, 39.1M, cut the output by hand (`| tail`,
  `| head`, `| sed`, `| grep`): the agent does not get the whole history anyway.
- Raw ledger reads: 814 turns, 15.5M (43 per 100 runs); 582 of them, 12.4M, name one item. By role: list items 7.9M, text
  rewrites 2.2M, Conductor subagents 1.0M, mod fixes 0.8M, Conductor window 0.8M. An earlier figure of 61.8M for ledger greps
  was too high (a loose rule).
- `modledger.packet_from` already builds such a packet for a mod, with a budget and a cursor: read it before writing
  (`src/RimMandrake/rimflow/modledger.py`, section `packet`). A list item has none: the Work brief says "Read it whole:
  cli.py show".

From `In-game fixer, and mod fixes and traces (172 sessions, 256M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Read the item's history and fold notes into a context | X | launcher pastes it (section 6, rank 6) | 41.9M `show`, all roles | A long item; the packet must not be cut silently |

From `3. Where the week went`:

| kind | found? | where |
|---|---|---|
| Re-derive a fact that a tool prints | yes, large | `--help` (51.3M), `show` cut by hand (39.1M), raw ledger reads (15.5M) |

From `List Pipeline: Shape, Work, Verify, Launch, View, Audit`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Work: read the item, do it, run its check, land, close | X | the Work brief lists five shell steps; the landing and close are M | part of 77.9M | The need can be wider than the check; the brief says so |

## spec

### What it must do

- A module, `src/RimMandrake/rimflow/item_packet.py`, folds an item into one text: state and title, the prose, the notes, the
  last runs and their evidence, the linked items and their states, the last commits that name the item, and the time of
  the reading.
- `detached_helper.brief_message` puts the packet in the brief of every detached launch.
- Over its budget it drops the oldest routine notes first. It always keeps: the last note, each note with his words, each
  `LEFT OPEN:`, `PROGRESS:`, `RULING` and `REFUSED` note, each fail run, and the open criteria.
- It says how many parts it left out, names them, and prints the command that shows them.
- A part that could not be read is named "could not look". An item that the ledger does not know gives a packet that says
  so; the launch still goes on.

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
- The risk (one page): *"The packet can omit the one decisive note. It must say what it left out."* The guard: the kept kinds
  above are never dropped; the text counts what it dropped and names the command; the test hides a decisive note among 100
  routine ones for each kind.
- It must not summarise or reword a note: a note is whole or it is left out and counted.
- It must not read `[]` as "could not look" or an unreadable ledger as "no notes".
- It must not give a blind judge, a fresh reader, an examiner, a challenger or the coverage judge the history: those always
  start fresh. The launcher leaves the packet out of their briefs, and a test names each of these roles.
- The budget (12,000 characters) guards one danger: text that stays in the context each turn. State it on the page.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank6_item_packet_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/16`, exit 1. Expected on a correct build:
`PASS 16/16`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: empty, unreadable, missing item, over budget (each decisive kind), spend talk, the reading time (stale). The
blind-role rule has no check in the script: the builder's selftest owes it.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-item-packet/boundary.md`. Selftest: `src/RimMandrake/rimflow/selftest_item_packet.py`.
Planted faults that the tests must catch:

- the newest note is dropped; a `LEFT OPEN:` note is dropped; a note is cut in the middle;
- the count of dropped parts is wrong or absent; the command is absent;
- `None` reads as empty; `[]` reads as could not look;
- a spend sentence passes; a blind judge's brief holds the packet;
- the packet is made from a ledger that is behind origin with no word about it.

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

- Must fall: `show` (1,615 turns, 41.9M; 85 per 100 runs) and `raw_ledger` (814 turns, 15.5M; 43 per 100 runs). Guess: about
  15M less a week, of 57.4M `[guess ~50%]`.
- Must not get worse: **work that an earlier run had already done or refused** (runs that end with "already done" or repeat a
  refused act). Baseline UNMEASURED: the builder reads the `result` texts of the baseline week's records for "already" first.
  Also the first load of a run (83.0k on average), which may rise by no more than the packet's own load.

## How it keeps improving

- `show` turns that still follow a launch within the first 10 turns: the packet lacks what they looked for.
- The share of packets that left something out, and how often the named command was then run.

## Size and order

Rank 6. Size: small. It enters the build pipeline now: its outcome check fails, it waits on nothing, so the List Pipeline's
launch step starts it. `RIMMANDRAKE_FILL_COMMANDS_INTO_BRIEFS_HELP_ASKED_2807_TIMES` edits the same launcher function; whoever lands second uses
`brief_message` as it stands.

## criteria

- The acceptance test prints PASS 16/16.
- The brief of one real detached run holds the packet (path on the item).
- The blind roles' briefs hold none (test names on the item).
