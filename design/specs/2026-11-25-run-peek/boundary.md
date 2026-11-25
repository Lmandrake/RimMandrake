# BOUNDARY: the peek at what each live mod run spends its time on, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/run_peek.py`, and its one call in the applied tick of
`src/RimMandrake/rimflow/maturation_dispatch.py`. The Conductor's start of turn runs `run_peek.py show`
(`src/RimMandrake/rimflow/roles/conductor.md` §Start of turn).
Item: `RIMMANDRAKE_PEEK_AT_LIVE_MOD_RUNS_HE_SAID_IT_IS_THE_CONDUCTORS_JOB`. The owner, 2026-11-24: "If they're spending a
lot of time on one or two tests, PLEASE let's ask if it's even sensible to try that, if it needs to be deferred,
re-examined, replaced with a simpler test, or needs to be raised with me".
Each promise has a check of its name in `src/RimMandrake/rimflow/selftest_run_peek.py`.

## ACCEPTS (the only inputs this is built for)

- **a-live-mod-run.** In the tick: each unit that the tick placed live on a mod (`facts[mod]["live_units"]`, from
  `maturation_now`'s run placement), read by its run record. In `show`: each detached run record with status
  `launching` or `running` whose mod is known: `RM_CONTROL_MOD` in its env, else the one mod whose DISPATCH shard grants
  its lease (`run_alive.mod_of`). A run with no mod is not a mod run and is not looked at.
- **a-test-table.** The mod's `design/concepts/<Mod>/version/test_table.json` in the run's clone, else in this repo. Its
  `tests` keys are the check ids.
- **a-transcript.** The run's own session transcript (`run_alive.transcript`). A tool call is an assistant `tool_use`
  line that is not a sidechain. Its time is the line's `timestamp`.

## How time is put on a check

- A tool call whose input names one or two check ids (whole words) puts the focus on those checks.
- A call that names more than two check ids, or claims or starts an item (`cli.py claim`, `cli.py start`), clears the
  focus. Such a call is bookkeeping across checks, not work on one.
- A call that names no check keeps the focus. After `LAPSE_CALLS` such calls in a row, the focus clears.
- The time from each call to the next call (to now, for the last call of a live run) goes to each check in the focus.
  The time of a long command, such as a scene run, is in the gap after that command.

## DOES NOT SURVIVE (not promised)

- **a-check-never-named.** A run that works on a check and never writes its id in a tool call puts no time on it.
- **work-in-a-subagent.** The parent's call that waits on a subagent counts for the parent's focus. The subagent's own
  calls are not read.
- **a-call-with-no-time.** A tool call whose line holds no readable `timestamp` puts no time on any check. The row
  counts such calls as `undated_calls`.
- **a-run-on-another-host.** A run on another machine reads blind with its host. Its transcript is not on this machine.

## PROMISES (each one is owed a check of the same name)

- **a-long-check-is-named.** A live mod run with `LONG_S` or more on one check is named, with the check, its minutes,
  the item, the run's last `PROGRESS:` note and its last message.
- **the-conductor-is-asked-once.** The tick writes one `LONG ON ONE CHECK:` line into the Conductor log and one Needs
  Conductor line, once for each run and check. The line asks the four questions: is the test sensible, defer it,
  re-examine it or replace it with a cheaper test, or raise it with him. A later tick does not write the same line again.
- **the-focus-lapses.** The time after `LAPSE_CALLS` calls that do not name the check is not put on that check.
- **bookkeeping-is-not-focus.** A call that names more than two checks, or claims an item, puts no time on any check.
- **a-blind-run-says-so.** A run whose transcript or test table cannot be read reads blind, with the cause. It is never
  a run with no long check.
- **the-tick-reads-its-own-runs.** The tick peeks only at the units of its own facts. It never lists every run record
  (2.1 s on `D:` for 1460 records, measured 2026-11-25), and a test tick never reads a real run.
- **one-run-never-stops-the-others.** A run whose look raises reads blind. The other runs are looked at.
- **the-peek-fails-quiet-in-the-tick.** A peek that raises writes `peek_error` into the tick's reading. It never costs
  the tick.
- **live-says-the-tick-runs-it.** `run_peek.py live` exits 0 only when the tick's reading holds a peek block younger
  than `FRESH_S` with no `peek_error`; 1 when it does not; 2 when the reading could not be read.
- **it-changes-no-run.** It stops no run, launches nothing, and writes no rimflow note.

## LIMITS

- `LONG_S` 3600 s: the item's title asks for a program that names a run with over an hour on one check. This is not a
  limit on the run; it is the point at which the Conductor is asked. Measured over 3 days of mod runs to 2026-11-25
  (`LAPSE_CALLS` 10): 4 runs passed it, the largest `sc_barrage_perf` at 349 min in one ExplosiveKnockback visit.
- `LAPSE_CALLS` 10: without a lapse, the 50 minutes of publishing after the last `sc_pawn_height` call of the FlowWorks
  visit-thirteen route run (2026-11-25) counted as work on that check (79 min against 30 min with the lapse).
- `FRESH_S` 900 s: the tick runs each 60 s. A peek block older than 15 ticks means that the tick does not run it.
