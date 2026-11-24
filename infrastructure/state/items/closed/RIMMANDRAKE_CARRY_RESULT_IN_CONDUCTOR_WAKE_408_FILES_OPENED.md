# RIMMANDRAKE_CARRY_RESULT_IN_CONDUCTOR_WAKE_408_FILES_OPENED

The run-end wake of the Conductor window carries the run's whole last message and one block of the state.

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
| 5 | **Conductor wake.** The wake carries the run's result and the state. Today 408 turns a week open result files `[measured]`. | 18M `[guess ~55%]` | small | A long result fills the window. Nothing decisive may be cut. |

The row of the ranked table:

| rank | candidate | pool `[measured]` | saved in a week `[guess]` | build |
|---|---|---|---|---|
| 5 | Conductor wake carries the result and the state | 54.8M (11.2 + 4.2 + 18.6 + 20.8) | ~18M ~55% | small |

The paragraph of the analysis:

> 5. **Conductor wake.** The run-end wake file carries the result's last message whole (the transcript has it), and the
> window gets one state block (locks, pipe line, accounts) at wake. Then a window reads a run's result without a turn
> (408 turns a week). Risk: long results grow the window's context; cap by relevance, never by cutting text. A result
> with a decision for him must not be treated as routine.

The Conductor window's turns (`cond.py`; 136 sessions, 193.7M) `[measured]`: other 2,534 turns, 66.4M; text to the owner 1,361, 33.6M;
owed list and wake reading 564, 20.8M (37k each); state reads 560, 18.6M (33k each); start 127, 17.8M; fetch a run result 408,
11.2M (27k each); publish 271, 7.1M; ledger 264, 6.7M; launch helper 193, 6.3M; then a report turn 170, 4.2M; write brief 45,
2.0M; log 85, 1.9M; open page 43, 1.3M.

Sessions that were read:
- Conductor window (136 sessions, 193.7M) and its subagents (169, 102.0M). Read: sessions ef311d37 (all 232 turns), aab6064a, 8c581a3a.

How a wake works today `[measured: src/RimMandrake/rimflow/run_end_wake.py]`: `detached_helper.finish` calls
`wake_conductor`, which posts `pending/<unit>.json` with the unit, the state, the result path and the item. The window's
Stop hook takes the file and prints one line per run ("... ended ...; item ...; full result: <path>") on stderr with exit 2.
The window then opens the `.out.json` with ad hoc Python. `detached_helper.run_report(rec)` already builds the run's whole
report, late turns included: use it.

From `Conductor window (136 sessions, 193.7M) and its subagents (169, 102.0M)`:

| job | class | the program, and does it exist | load | risk |
|---|---|---|---|---|
| Wake: owed list, handoff, words, pipe, locks | M | `seat_restart.py words`, `queue --owed` exist; the window opens and cuts them by hand | 20.8M | A pasted wake that is long costs on each later turn; keep it short |
| Read a run's result after a wake | M | the wake file carries the unit, state and path only; the window opens the `.out.json` with ad hoc Python, 408 turns | 11.2M + 4.2M of report turns | The result text can hold what he must see; the packet must not cut it silently |
| State reads (pipe, locks, accounts, MATURATION_NOW) | M | commands exist; a standing block in the wake is not built | 18.6M | A stale block must carry its time |
| Talk to him; decide; open pages | J | stays | 33.6M | — |
| Launch helpers; write briefs | X | `detached_helper.py launch` exists | 6.3M + 2.0M | — |

From `3. Where the week went`:

| act | turns | weighted tokens | share |
|---|---|---|---|
| State reads (pipe, units, accounts) | 3,106 | 51.5M | 3.0% |

## spec

### What it must do

- The wake text holds each ended run's last message, whole (`run_end_wake.report_of`, with `detached_helper.run_report`'s rule
  for a run whose report stands before a late remark).
- A run that failed, ended empty, could not be read, holds `LEFT OPEN:` or is owed stands first; routine results stand after.
- One state block ends the wake text: who drives each game, the pipe line, the accounts. Each line carries the local time of
  its reading. Account lines say how much is LEFT, one line for each account.
- Each reader has a deadline. A reader that fails or hangs reads COULD NOT LOOK with its name, and the wake still goes out.
- **First act:** measure how much hook text reaches the window. Post a wake with 100,000 characters to a test window and read
  in its transcript what arrived. If the harness cuts it, the wake writes the whole text to one file and gives its head, its
  tail, the path and "N characters are in the file"; the decisive runs go in the uncut part. Write the reading on the page.

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
- The risk (one page): *"A long result fills the window. Nothing decisive may be cut."* The guard: no text is cut; what does not
  fit goes to a file that the wake names, with the count. The order puts the runs that need a hand first.
- It must not summarise, judge or answer a result, and must not call a result routine when it holds a question, a decision
  for the owner, `LEFT OPEN:`, OWED or a failure.
- It must not carry the `.out.json`'s spend fields. (The state block's account lines are for the Conductor window, which is
  not a launched agent; they never go in a brief.)
- A stale state block must not read as now: each line has its time.
- It must not delay or lose a wake: a reader that hangs never holds the post, and the restart drain rule stays.

## verify

### Acceptance test

```
python3 design/specs/2026-11-23-agent-work-to-code/acceptance/rank5_wake_result_accept.py
```

Expected today: FAIL. Seen failing on 2026-11-23 on base `9d89f50304`: `FAIL 1/15`, exit 1. Expected on a correct build:
`PASS 15/15`, exit 0. The script's head holds the contract: the module, the functions, the arguments and the return values.
The test was also run against a throwaway stub outside the repo: every check passed except the checks that need the page,
the listed selftest and the wiring, so the contract can be met `[measured]`. Do not edit the script to pass it. If one of
its checks is wrong, repair the check with a planted fault that it catches and a correct build that it passes, and put
both readings on this item. Do not move the script: the outcome check of this item runs it at this path.

One check passes today (no spend figure reaches the wake): it must stay green. It covers: value, long, empty, missing, torn,
failed, a reader that raises, a reader that hangs, an empty reader.

The live part (a real wake into a real window): the builder reads one wake in the Conductor window's transcript and puts its
path and time on the item. Acceptance test of that part: none, live window behaviour.

## How we know it is written well

The builder writes the boundary page before any code (`design/RimMandrake/standing_rulings.md` §A boundary page before
pipeline code): ACCEPTS, DOES NOT SURVIVE, PROMISES (each promise has a test of its name), LIMITS (each number names its
danger and its evidence). The selftest goes in `src/RimMandrake/Utils/pipeline_tests.json`, and so does the acceptance
script when it is green. One fresh reader who did not make the change reads the changed pipeline files once.

Page: `design/specs/2026-11-23-wake-carries-result/boundary.md`. Selftest:
`src/RimMandrake/rimflow/selftest_run_end_wake_result.py`. Planted faults that the tests must catch:

- the text is cut at any length; an empty message reads as could not look; a torn file reads as empty;
- an error result reads as a value; the decisive run stands last;
- a reader that hangs holds the wake; a reader that raises is left out; a block line has no time;
- `total_cost_usd` reaches the text.

## How we measure that it helped

The baseline below is the week to 2026-11-23, 7:56 PM PST. On 2026-11-23, about 8:30 PM PST, the report commands were run
again over the kept census data and gave the same numbers `[measured]`. The command that made them:

```
cd /mnt/d/ClaudeWork/rimmandrake/scratch/a2c && python3 cond.py
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

- Must fall: `fetch_result` (408 turns, 11.2M) and `report_after_fetch` (170 turns, 4.2M), `state_reads` (560 turns, 18.6M),
  `wake_reading` (564 turns, 20.8M). Guess: about 18M less a week, of 54.8M `[guess ~55%]`. A good result is `fetch_result`
  under 100 turns a week. Compare per 100 Conductor sessions (136 in the baseline).
- Must not get worse: **results that nobody acted on** (runs with `owed_close` set, or a `LEFT OPEN:` note, that no Conductor
  event or continuation followed within 24 h). Baseline UNMEASURED: the builder counts the baseline week first. Also the
  average turn of the Conductor window (25k to 37k): a long wake that stays in the context raises it.

## How it keeps improving

- `fetch_result` by session: a window that still opens `.out.json` files shows what the wake lacks.
- COULD NOT LOOK lines in the wakes of the week, by reader: a reader that moved.

## Size and order

Rank 5. Size: small. It enters the build pipeline now: its outcome check fails, it waits on nothing, so the List Pipeline's
launch step starts it. No other item edits its files.

## criteria

- The acceptance test prints PASS 15/15.
- The reading of how much hook text reaches a window is on the page.
- One real wake carried a whole result (transcript path and time on the item).
- The close carries `--live "hook=run_end_wake.py"`.
