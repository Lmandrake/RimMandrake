# BOUNDARY: the spend cap a detached launch carries, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`main`'s `launch` arguments, `earlier_cap`). Items:
`RIMMANDRAKE_FIX_THREE_TOOL_DEFECTS_LESSONS_DID_NOT_STOP` and `RIMMANDRAKE_REQUIRE_HELPER_SPEND_CAP_FIFTEEN_STOPPED_FOUR_RUNS`,
written 2026-11-19. `launch` defaulted `--budget-usd` to `DEFAULT_BUDGET_USD = 15.0`, and `--resume` did not carry the
earlier run's cap: the default level stopped at least four real runs (Crystallize 2026-W47, sweeps §5 cluster 8;
`infrastructure/state/lessons/20261115T183415Z-BENCH-detached-helper-py-launch-refuses-item.md`,
`20261117T142459Z-BENCH-relaunch-keeps-default-budget.md`, `20261119T001144Z-BENCH-detached-lane-several-tickets-launched-default.md`).
Under `design/RimMandrake/standing_rulings.md` §No limit without the danger it guards, the per-run stop stays (his
order, below) and the default LEVEL goes: no default number is kept, because nothing measured says a run past it is a
runaway. A launch states its cap, as `maturation.py launch` already must. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_detached_helper.py`.

## ACCEPTS (the only inputs this is built for)

- **a-launch-command-line.** `detached_helper.py launch` arguments, with or without `--budget-usd USD` and `--resume
  SESSION`.
- **the-run-records.** The run records under `<RM_DISPATCHER_STATE>/detached/` that earlier launches wrote: their
  `budget_usd`, `at`, and the session each ran (`session`, `resume_session`, or the `session_id` in its result file).

## DOES NOT SURVIVE (not promised)

- **a-session-run-outside-detached-helper.** A session that no run record holds (a window's own session, or a record
  deleted) has no earlier cap to carry: that resume is refused and must state `--budget-usd`.
- **direct-python-callers.** `launch()` called from Python takes the cap as an argument (`left_open_continue.py` and
  `stop_resume.py` pass the run record's); only the command line is checked here.

## PROMISES (each one is owed a test of the same name)

- **a-launch-without-a-cap-is-refused.** A `launch` with neither `--budget-usd` nor `--resume` exits 2 before anything
  runs (no fetch, clone, unit or record) and its refusal names `--budget-usd <USD>` and `--budget-usd 0`.
- **an-explicit-cap-is-carried-unchanged.** `--budget-usd 0` (no cap) and `--budget-usd 40` reach the launch as 0.0 and
  40.0; a negative cap is refused (exit 2).
- **a-resume-carries-the-earlier-cap.** A `launch --resume SESSION` without `--budget-usd` launches with the
  `budget_usd` of the newest run record of that session (0 carried as 0), and its text names the record it took the
  cap from.
- **a-resume-with-a-cap-takes-the-stated-cap.** A `--resume` with `--budget-usd` launches with the stated cap.
- **a-resume-whose-earlier-cap-cannot-be-read-is-refused.** A `--resume` without `--budget-usd` whose session no record
  holds, or whose newest record has no numeric `budget_usd`, exits 2 before anything runs, naming the session and
  `--budget-usd`; it never falls back to a number.

## LIMITS

- **the per-run spend stop** (`spend_watchdog.wrap`, any cap > 0). Danger: an unattended run burning without end.
  Evidence: the owner's order, *"not burn 90M tokens overnight by itself"* and *"Don't let any burn go to 90M this
  time ok?"* (2026-11-12/13, `standing_rulings.md` §No launched agent is told its spend); it is not lifted here. Its
  level is the launcher's, stated per job; there is no default level. The cap never reaches the agent's brief.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
