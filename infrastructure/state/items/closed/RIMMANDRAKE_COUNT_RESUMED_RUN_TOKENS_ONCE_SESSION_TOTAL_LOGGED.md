# RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED

Filed 2026-11-19 by the night-hypotheses run (`RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER`), found
by a read-only replay. Not fixed by that run: its brief forbade any edit to pipeline code.

## spec

**The defect.** A detached run launched with `--resume <session>` gets a result JSON whose `modelUsage` is the whole
claude session so far, the earlier runs of that session included. `detached_helper.outcome()` passes that result to
`role_launch.run_tokens()`, whose docstring reads `modelUsage` as "the whole process", and records the figure as this
run's `tokens`. So a resumed run's record, its `DETACHED RUN ENDED` line in the Conductor log, and every sum built on
either, count the earlier runs of the session again.

**Measured, 2026-11-19, two instruments that agree:**
- Run records (`D:\ClaudeWork\rimmandrake\dispatcher\detached\*.json`, runs ended since 2026-11-18 00:00 PST): 26 of
  26 resumed runs that follow an earlier run of their session record more than their own part; the sum is overstated
  by 81,158,999 weighted tokens [measured: `check_resumed_run_tokens.py`, below].
- Session transcripts joined to the Conductor log by clone and end time: the logged figure equals the transcript's
  cumulative spend for the same 26 runs (to within one token for 24 of them) and never the run's own time window;
  logged 150.2 million, own windows 68.9 million [measured: `design/experiments/2026-11-19-night-hypotheses/tools/log_runs.py`].
  The 87 runs that did not resume match both readings, so the instrument can see a correct run.
- One pair read by hand: unit `...-1795058457` (stopped at its cap) reports `cacheReadInputTokens` 18,249,459 and
  `outputTokens` 90,044; the run that resumed its session, `...-1795059567`, reports 29,525,128 and 125,389.
- Scale: the Conductor log's run lines since 2026-11-18 00:00 PST sum to 373.6 million weighted tokens; the same
  runs' transcripts hold 309.1 million.

**What is wrong downstream is not measured.** Anything that sums run `tokens` inherits it: the day's spend, a
per-item spend, `overspend_day`, the "52.8 million on review tickets" and "303.5 million, 86 runs" figures quoted in
`design/specs/2026-11-18-review-growth-cycle/01-design.md`. Also not checked: whether `spend_watchdog` reads the same
cumulative figure for a resumed run, which would stop a resumed run early against a cap meant for one run.

**The fix, in outline (the builder decides the form).** A resumed run's `tokens` is this run's part only: the
session total its result reports, less the largest session total an earlier run of the same session reported. When
the earlier total cannot be read, the run's tokens are UNMEASURED with that cause, never the session total. The record
keeps the session total under its own name, so the correction is checkable. Old records are not rewritten; a reader
that sums across the fix date says so.

## verify

Acceptance test, a runnable command, watched FAIL on the base (commit `361ec1975a`, records of 2026-11-18):

```
python3 design/experiments/2026-11-19-night-hypotheses/tools/check_resumed_run_tokens.py . \
    /mnt/d/ClaudeWork/rimmandrake/dispatcher/detached --since <ISO time the fix landed>
```

- Base, `--since 2026-11-18T08:00:00Z`: `VERDICT FAIL: 26 of 26 resumed runs record more than their own part`, exit 1.
- Pass: `VERDICT PASS: N resumed runs, each records its own part only`, exit 0, with N at least 1. Expected pass
  count: 1 verdict line, N = every resumed run since the fix.
- `VERDICT EMPTY` (exit 4) is not a pass: no resumed run has ended since the fix. Seen on the base with a future
  `--since`. `VERDICT COULD-NOT-LOOK` (exit 3) is seen with a missing folder and with an unreadable `--since`.
- The builder also writes the offline selftest with the fix (standing ruling: the test is built with the item): a
  synthetic pair, an earlier run whose result totals A and a resumed run whose result totals A+B, must record B; a
  resumed run whose earlier total is unreadable must record UNMEASURED; a run that does not resume must record its
  whole result, unchanged. That selftest covers the three input kinds; the command above covers real records.

## criteria

- A resumed run's record and log line carry its own part only.
- A run that does not resume is recorded exactly as today.
- "Could not read the earlier total" is UNMEASURED with its cause, not zero and not the session total.
- The instrument trap is written into `infrastructure/state/facts/instrument_traps.md`: a sum of run tokens across
  2026-11-18 or earlier counts resumed sessions more than once.

## refs

file: src/RimMandrake/rimflow/detached_helper.py
file: src/RimMandrake/rimflow/role_launch.py
file: design/experiments/2026-11-19-night-hypotheses/tools/check_resumed_run_tokens.py
