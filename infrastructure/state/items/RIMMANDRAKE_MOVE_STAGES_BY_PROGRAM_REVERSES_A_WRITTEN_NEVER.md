# RIMMANDRAKE_MOVE_STAGES_BY_PROGRAM_REVERSES_A_WRITTEN_NEVER

A program advances a mod when every row counts, and files a skeleton ticket for each failed row.

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
| 8 | **Stage moves.** A program advances a mod when every row counts. It files a skeleton ticket for each failed row. | 10M `[guess ~50%]` | medium | It can advance on checks that are wrong together. A steward still reads any look. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 8 | Program advances, road back, walk-brief data | 25.4M in 39 steward runs | ~10M ~50% | medium |

The paragraph of the analysis:

> 8. **Stage confirm and road back.** The tick advances when the exit program reads "met" with no unclassed row, files a
> skeleton for each MOD row, and wakes a steward only for a look, a joined cause or a wrong check. It reverses a
> decision in `maturation_dispatch.py` ("the program never advances"). So it needs the Conductor's word. Risk:
> advancing a mod on rows that are wrong in the same way (the check was wrong): the steward found such cases.

Runs that were read:
- Steward: confirm, road back, pre_human, preflight (39 runs, 25.4M). Read: CONFIRM_GIMMESOMESLACK_VISIT_THREE, CONFIRM_PYRELANDS_CYCLE_FOUR, ROUTE_GIMMESOMESLACK_VISIT_ONE, ROUTE_PYRELANDS_CYCLE_THREE, STEWARD_EXPLOSIVEKNOCKBACK_PRE_HUMAN.

More readings. By item name and stage from the run records (`rows.pkl`, this filing) `[measured]`: CONFIRM runs 12, 5.4M (in_game 6,
blind_challenge 4, offline_build 2); STEWARD runs at pre_human 6, 4.9M, and at preflight 2, 2.0M; ROUTE runs that the tick launched
27, 12.5M (in_game 25, blind_challenge 2); ROUTE runs launched by hand 10, 15.0M. The analysis counts 19 road-back runs, 13.2M: no
census script prints that sum, and this filing could not make it again, so the number of road-back runs is UNMEASURED
between 19 and 27. The two figures of cost agree within 0.7M.

**The written decision that this item reverses**, word for word on `9d89f50304`:

- `src/RimMandrake/rimflow/maturation_dispatch.py:44`: "ready         every exit test passes: "ready to advance" for the
  Conductor; the program never advances"
- `src/RimMandrake/rimflow/maturation_dispatch.py:1893` to `1896` (`decide_blind`): "The owner's condition, 2026-11-14 ~9 PM PST:
  "As long as we don't have automated loops rejecting/cycling things, we can't get into too much trouble." ... every ended cycle
  (exit met, not met, or no exit block) is a Needs Conductor line, and the program never advances: the steward's confirmation
  stays a hand step."
- `src/RimMandrake/rimflow/maturation_dispatch.py:1925`: "advance %s --to in_game --steward-confirms \"...\" (a Conductor step; the
  program never advances)"
- `src/RimMandrake/rimflow/maturation_dispatch.py:2058` (`decide_ingame`): "Every ended visit is a Needs Conductor line; the program
  never advances and never takes the bridge itself."
- `src/RimMandrake/rimflow/maturation_dispatch.py:2087`: "(a Conductor step; the program never advances)"

The ruling must say: may the program advance a mod on an exit that it computed; at which stages; and does the owner's
condition on automated loops allow a program to send a mod back a stage. The ruling reads the measurement of the small items
first. An open item nearby: `RIMMANDRAKE_PASS_OWNER_ITEMS_ON_ROAD_BACK_ULLAI_HELD` (a road back that an owner item holds).

From `Steward: confirm, road back, pre_human, preflight (39 runs, 25.4M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Confirm the exit (12 runs): read rows, table, SUMMARY; say the exit is met; advance | X | `build_match` and `next` compute the exit; `maturation_dispatch.py:1896` says "the program never advances: the steward's confirmation stays a hand step". Move: the program advances when each row counts, no row is unclassed, and each strange row has a class | 5.4M | The steward also judges looks (it ran a blind look judge) and can find a wrong check. Keep those as a judge run only when a row asks |
| Road back (19 runs): read failed rows, file an item for each, advance to an earlier stage | X | Rows are classed by the driver; the program files a skeleton item for each MOD row with check, row, evidence, expected class, then moves the stage | 13.2M | Two rows with one cause make two tickets; the agent joins them. The program can list same-cause rows by check family |
| Pre_human walk brief (8 runs) | J, with a filled template | `walk_brief.md` is a template; the list of open tickets and last rows is data | 6.9M | "What I noticed first" is judgement |

From `3. Where the week went`:

| kind | found? | where |
|---|---|---|
| Choose the next act from a state | mostly built (`mod_next`, `list_pipeline`) | the stage confirm is still an agent |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| Stage record tools | 5,932 | 94.9M | 5.5% |

## spec

### What it must do

- `src/RimMandrake/rimflow/stage_confirm.py` reads the exit, the rows, the build match and the classes, and gives one act:
  advance, road back, steward, wait, blind or off.
- **Advance**: the exit program reads met, the build matches, every row is PASS, no row is unclassed, no look is owed, and no
  check was edited in this visit.
- **Road back**: each failed row has the class MOD. The program files one skeleton item for each row (check, row, evidence,
  expected class) and moves the stage. Rows of one check family are listed beside each other as "same cause?"; the agent
  joins them.
- **Steward**: anything that needs a reading: a look, an unclassed row, a wrong check, a wrong scene, a COULD NOT LOOK row, or
  a check that was edited in this visit. The launch says which.
- The walk brief's data (open tickets, last rows) is filled by the program; "what I noticed first" stays with the agent.
- The tick calls it in place of its "Needs Conductor" line for an ended cycle or visit, and the act goes in the daily digest.

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
- The risk (one page): *"It can advance on checks that are wrong together. A steward still reads any look."* The guard: a check
  edited in this visit sends the visit to a steward, and so does any look. The steward found such cases before
  `[analysis]`.
- It must not class a row, choose the stage to return to against the road-back rule, or join two tickets.
- It must not advance on COULD NOT LOOK, on an empty table, on rows from before the run's end, or on another build.
- It must not move a mod that the owner holds, that `./pipe off` stops, or that is at his walk: the pass at his walk is his.
- It must not loop: one road back for one ended run, and the owner's condition on automated loops stands as ruled.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank8_stage_moves_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/16`, exit 1. Expected on a correct build:
`PASS 16/16`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

One check reads `Ruling: <event or item>` on the boundary page: it fails until a ruling is written there. It covers: all pass,
unclassed, look, wrong check, wrong scene, could not look, edited checks, unreadable, empty, stale, held.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-stage-confirm/boundary.md`, with the line `Ruling: <ledger event or item>`. Selftest:
`src/RimMandrake/rimflow/selftest_stage_confirm.py`. Planted faults that the tests must catch:

- an unclassed failure advances; a COULD NOT LOOK row advances or goes back; an empty table advances;
- an edited check does not reach a steward; a look does not reach a steward;
- two MOD rows make one skeleton; a skeleton has no evidence;
- stale rows or another build advance; a hold is ignored.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 kinds2.py; python3 launch.py
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

- Must fall: the steward runs (12 confirm, 5.4M; 8 walk brief and preflight, 6.9M; 19 to 27 road back, 12.5M to 13.2M; 25.4M
  in all). Guess: about 10M less a week `[guess ~50%]`. `window.py` has no key for these: this item adds `steward_runs` by
  item name and stage (the rule of this filing: names that start CONFIRM, ROUTE, STEWARD), with its check, and makes the
  baseline again with it.
- Must not get worse: **mod moves that were undone** (a stage move that the Conductor or a later run reversed within 7 days).
  Baseline UNMEASURED: the builder counts the baseline week from the stage records first. Also the hours between an ended
  run and its stage move, which should fall.

## How it keeps improving

- Stage moves by the program that a person reversed: one is a defect to fix at its cause, not a number to watch.
- The share of visits that go to a steward, by ask: an ask that is always answered the same way can become a rule.

## Size and order

Rank 8. Size: medium. **This item waits.** Its reason: waits until the small items are built and their 7-day measurement is
read. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads the measurements and decides which waiting item
goes next. The small items are ranks 3, 5, 6, 7 and 10. A builder does not start this item before that decision.

**It also needs a ruling.** No builder starts it before the owner or the Conductor rules on the reversal below. Its ledger
split holds a part that is routed to the Conductor, so the List Pipeline launches nothing on it.

## criteria

- A ruling is on the ledger and on the page.
- The acceptance test prints PASS 16/16.
- The five quoted lines of `maturation_dispatch.py` were changed to say what is now true.
