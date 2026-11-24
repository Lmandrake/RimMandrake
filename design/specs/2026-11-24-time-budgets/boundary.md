# BOUNDARY: time budgets in pipeline machinery, Design Version 0.1.0

Code: `src/RimMandrake/Utils/time_budget.py`, `src/RimMandrake/Utils/time_budget_lint.py`,
`src/RimMandrake/Utils/time_budgets.json`. Tests: `src/RimMandrake/Utils/selftest_time_budget_lint.py`.
The guard on progress: `design/specs/2026-11-24-progress-guard/boundary.md`.
Item: `RIMMANDRAKE_MEASURE_TIME_BUDGETS_AGAINST_REAL_RUNS_HE_SEES_TEN_PERCENT`. Census: `census.md`.

Owner, 2026-11-24: *"Aren't time budgets for detecting out-of-control or stuck programs? Why do we have them set to within
10% of what the process really needs?"*

## ACCEPTS

- **a-budget-with-a-name.** A number with a name that the lint knows (`NAME` in `time_budget_lint.py`): a `timeout=`
  argument, a constant, a parameter default, an argparse default, a `.json` key, a systemd `Timeout*Sec`,
  `RuntimeMaxSec`, `WatchdogSec` or `--max-seconds`, a shell `timeout N`.
- **a-file-in-scope.** A tracked file that `pipeline_files` of `pipeline_tests.json` matches, or that `ALSO` of the lint names.

## DOES NOT SURVIVE

- **a-budget-with-another-name.** A wait loop that counts its own polls, and a number with no telling name, are not found.
- **a-number-set-at-run-time.** A budget that a program computes, or reads from the environment, is not found.
- **a-budget-inside-a-test.** The selftests and the acceptance programs are not read. The guard of the runner ends them.

## PROMISES (each one is owed a test of the same name)

- **no-danger-is-refused.** A new budget whose tag names no danger, or no longest run, is RED. So is one with no tag.
- **tight-is-refused.** A budget under `FACTOR` times the longest run that its tag (or its class) names is RED.
- **one-constant.** `time_budget.FACTOR` alone sets the number.
- **stays-green.** A tag with an UNMEASURED longest run, a tag with `stays=<reason>`, a name from `time_budget.py`, and a
  number that is no time budget are green.
- **known-stands.** A budget of `time_budgets.json` stands at its value or higher.
- **lowered-is-refused.** A lowered budget is a new budget.
- **added-is-refused.** One more budget in the same place is a new budget.
- **known-is-held-to-the-factor.** An entry that holds a `longest_s` is held to `FACTOR`.
- **blind.** A scan that finds no budget reads UNMEASURED (exit 2), never green.
- **the-tree.** This tree is green.

## LIMITS

- `time_budget.FACTOR = 10`: the owner's line may change; this is its one place.
- `publish.CHECK_CAP_S` and `timeout_s` of both check lists, 6000: the backstop of one door check. Danger: a test in an
  endless loop holds a landing. Longest real run: 599 s at load 45.
- `time_budget.CLASSES`: each class holds its danger, its evidence and its longest real run.
- At load 40: a guard on progress does not change with the load, because a live child gets some CPU time in 30 minutes.
  A raised budget holds while the loaded run is under 10 times the longest run on record. The records are of a machine at
  load 20 to 50 for most of the 14 days. `selftest_maturation_autonomy.py` took 16 times its idle run at load 45, and the
  6000 s backstop is 10 times that loaded run.
- `METRONOME`: one beat may hold the beat lock up to 1500 s. A phase is no longer deferred because a sibling is slow. The
  `max_ok_age_s` of a critical phase still alarms at 300 s or 600 s; an alarm ends no work.
- What stays under 10 times, each with its reason: the job deadlines of SteveDesktop that
  `testq.py`, `brake_release.py` and `visit_feed.py` submit (21600 s, 5.3 and 8.5 times). A worker at an older commit
  refuses a job over 21600 s before it syncs.
- 270 budgets have no record of a real time. They stand as they were (`time_budgets.json`), and nothing reached them in the
  14 days as far as the journal and the agent transcripts show. A measured run that comes later goes in as `longest_s`.
