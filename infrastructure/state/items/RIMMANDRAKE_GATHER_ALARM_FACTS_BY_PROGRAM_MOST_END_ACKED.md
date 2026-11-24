# RIMMANDRAKE_GATHER_ALARM_FACTS_BY_PROGRAM_MOST_END_ACKED

A program gathers the facts of an alarm, and answers the steady ones.

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
| 9 | **Alarms.** A program gathers the facts of an alarm and answers the steady ones. | 10M `[guess ~50%]` | medium | A slow rise inside the normal band is seen late. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 9 | Incident packet, and program routes for steady incidents | 37.8M in 194 run records; 21.5M ended in an ack | ~10M ~50% | medium |

The paragraph of the analysis:

> 9. **Incident packet.** The program writes the metric's definition, the readings, the owner of the cause and what the
> last run wrote; a route table answers "steady, expected" for more than the five routes. The clock to clear and the
> five bands stay as decided. Risk: a slow rise inside a band (named in the boundary page as accepted).

Runs that were read:
- Operations (97 sessions, 18.0M) and quick checks (49, 14.0M). Read: Operations sessions 951770a7, 580daa95, 27965b23, b8ca2bdc and 12 result texts; Conductor sessions 41470598, 312e50f2, 421ce59c and 12 result texts.

What the role runs ended with (`outc.py`; its import path was repaired to run it again on 2026-11-23) `[measured]`:

- Operations, 132 run records, 20.6M: re-read and re-acked 47, 11.7M; read and no act 48, 3.2M; fixed code 24, 4.7M; other 13,
  1.0M.
- Conductor role, 62 run records, 17.2M: re-read and re-acked 40, 9.8M; fixed code 11, 3.9M; read and no act 9, 2.9M; other 2,
  0.6M.
- Together 194 records, 37.8M; 87 of them, 21.5M, ended in an ack (57% of the cost).
- Reading the readings and the metric definitions: 1,048 turns, 9.2M (Operations 5.9M, Conductor quick checks 3.3M). Writing the
  ack, the line, the note: 356 turns, 3.4M (`p4.py`).

**What is built already, and not to be built again:** `design/specs/2026-11-19-incident-news-and-program-routes/boundary.md`
(Design Version 0.1.0). Five repeat alarms have a banded program route (`incident.program_answer`): `steve.incident_unclaimed_min`,
`accounts.lukas.runway`, `wrapup.debris_standing`, `maturation.idle_owed_max_min`, `disk.scratch_dirty_end`. A clock that only
aged is not news. `alarm_routes.json` holds 84 routes: 23 lines read `"route": "program"` on 2026-11-23 `[measured]`; the analysis says 18
program routes and 61 role routes. That page accepts one loss by name: a step inside the band is seen late.

From `Operations (97 sessions, 18.0M) and quick checks (49, 14.0M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Decide that a repeat alarm has not changed | M, part built | `incident.py` `program_answer`: 5 routes. 18 program routes and 61 role routes exist | Operations 47 runs 11.7M and Conductor 40 runs 9.8M ended in an ack | A step inside a band that is a real start of a fault |
| Find what a metric is: read `ops_watch.py`, series, `told.jsonl`, past acks | M | an incident packet built by the program, with the metric's definition and last readings. Not built | 9.2M of 1,048 turns | The definition line can go stale; take it from the code |
| Find the cause of a new alarm, fix it | J | stays (24 Operations runs, 4.7M, ended in a fix) | 4.7M | — |
| Write the ack, the plan, the trigger line | X | fill the row from the packet; the plan stays | 3.4M | A plan that names no new act is worth nothing |
| Fold overdue hand acts, note a steady state | M | `maturation_hands.py` exists | UNMEASURED | Wrong item folded |

From `3. Where the week went`:

| kind | found? | where |
|---|---|---|
| Write a report that a template could write | yes | incident acks, stage confirm, some wakes |

## spec

### What it must do

- `src/RimMandrake/rimflow/incident_packet.py` gathers the facts of an alarm before the agent starts: the metric's definition with
  the code line it comes from, its last readings with their ages, who owns the cause, and what the last runs wrote.
- The launcher puts the packet in the alarm run's brief. The plan and the trigger line are blank for the agent.
- A banded program route answers "steady, expected" only when the last reading is MEASURED, inside the band, fresh, and does
  not rise slowly across the days that the route names.
- New program routes come from the alarms that the week's runs acked with nothing to fix; each route states its band, its
  runbook line, its age limit and the evidence for the band.
- Each reader has a deadline; a part that could not be read is named, and the alarm then goes to the agent.

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
- The risk (one page): *"A slow rise inside the normal band is seen late."* The guard: the slow-rise rule (days and share of the
  band) sends it to the agent; each route states both numbers with their evidence.
- It must not answer an alarm on a reading that is UNMEASURED, stale, empty or unreadable: those go to the agent, each with
  its own cause.
- It must not write a plan, a cause or an ack text in the agent's name.
- It must not move the clock to clear or the five bands that the owner decided by card (2026-11-19) without a ruling.
- It must not take the definition from a page: the code line is the source, and a definition that is not found reads could
  not look.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank9_alarm_facts_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 0/15`, exit 1. Expected on a correct build:
`PASS 15/15`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

It covers: steady, out of band, slow rise, UNMEASURED, stale, unreadable, empty, no band, role route, a hung reader, a reader
that raises.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-alarm-facts/boundary.md` (it extends the incident page; it does not repeat it). Selftest:
`src/RimMandrake/rimflow/selftest_incident_packet.py`. Planted faults that the tests must catch:

- an unreadable reading answers as steady; an empty series answers as steady; an old reading answers as steady;
- a slow rise answers as steady; a role route is answered by the program;
- a definition from a page that the code no longer says;
- a reader that hangs holds the alarm.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 outc.py; python3 p4.py
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

- `outc.py` needs its import path repaired to run (it names a clone that is gone), and `window.py` has no key for the outcomes
  of role runs: this item adds `ops_ack_runs` (the rule of `outc.py`), with its check.
- Must fall: role runs that end in an ack (87 runs, 21.5M in 194 records, 37.8M) and the definition-reading turns (1,048, 9.2M).
  Guess: about 10M less a week `[guess ~50%]`.
- Must not get worse: **missed alarms**: an alarm that a program answered and that an agent, the owner or a later reading
  showed to be a real fault; and incidents that relapse within 24 h. Baseline UNMEASURED for the first (no program answered
  before 2026-11-19 for most routes); the builder counts the relapses of the baseline week from the incident rows.

## How it keeps improving

- Program answers that a later agent run contradicted, by route: one means that the band is wrong.
- A sample each week: one agent reads 5 program answers blind and says if it would have acted. A disagreement reopens the
  route.
- Metrics with no definition found (could not look) in the packets of the week.

## Size and order

Rank 9. Size: medium. **This item waits.** Its reason: waits until the small items are built and their 7-day measurement is
read. `RIMMANDRAKE_READ_SMALL_ITEM_MEASUREMENTS_THEN_PICK_OF_FIVE` reads the measurements and decides which waiting item
goes next. The small items are ranks 3, 5, 6, 7 and 10. A builder does not start this item before that decision.

## criteria

- The acceptance test prints PASS 15/15.
- Each new route has a band, an age limit, a slow-rise rule and its evidence.
- The relapse baseline is on the item.
