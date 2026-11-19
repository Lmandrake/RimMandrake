# BOUNDARY: incident revisit news and the program-answered repeat alarms, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/incident.py` (`clock_unit_s`, `reading_moved`, `revisit_news`, `program_answer`, the
route test in `step`), the five banded `route: program` rows in `src/RimMandrake/rimflow/alarm_routes.json`, and the
alarm-run filter in `src/RimMandrake/rimflow/role_launch.py` (`program_answered`, the hold beside `recovering_keys` in
`decide_roles`). Item: `RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS`, written 2026-11-19, from the owner's card
of 2026-11-19 ("Fix the news bug", "Program answers 5 repeat alarms") and
`D:\ClaudeWork\rimmandrake\conductor\operations_role_analysis_20261117.md` sections 3, 4 and 5 (options c and f).
Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_incident_news.py`.

## ACCEPTS (the only inputs these readers are built for)

- **an-incident-reading.** `revisit_reads`' row per metric: `[standing?, class, value, measured?, signals fired,
  observed at]`, and the status times of two such rows (`revisit_status_t`), as `step` stores them on a revisit. A row
  stored before 2026-11-19 has no sixth field; its clock is graded over the status times, as before.
- **a-banded-program-route.** An `alarm_routes.json` route with `route: program`, a `band` (`min` and/or `max`, numbers,
  inclusive), a `runbook` line (the note the agent kept writing), and the `reader` and `cause` an out-of-band reading
  goes to. A program route with no `band` is the old kind: it never calls an agent, and these promises do not cover it.
- **an-ops-alarm-row.** An OPEN row of ops_watch `alarms.json` keyed `<TAG>:<metric>`, with its `item` (or none, for an
  alarm filed for Operations alone) and `worse_n`, read beside the same status snapshot's `points[<metric>]`.

## DOES NOT SURVIVE (not promised)

- **a-step-inside-the-band.** A real change of a banded count that stays inside its band (debris 2 to 11) is not news
  and calls no agent; it is caught when it leaves the band. The card's stated cost: "a real jump in those readings is
  caught one step later".
- **a-sixth-look-that-would-have-found-something.** While a repeat alarm's reading stays in band no agent re-reads
  it: a cause only a model would see in band is not seen. The card's stated cost: "a later look that would have found
  something is lost". The Operations scheduled runs and the daily incident ladder still read everything.
- **a-note-that-could-not-be-written.** The program's note goes through the dispatcher's ledger-note path; a note that
  path does not write (lock busy, tick budget spent) is journalled there and not retried by this code.
- **a-band-set-wrong.** The five bands are numbers from the measured series of 2026-10-27..2026-11-19 (each row's
  `_why`); a band that is wrong only moves when a person edits the row.

## PROMISES (each one is owed a test of the same name)

- **a-clock-that-only-aged-is-not-news.** A metric whose value is "how long" (`_min`, `_h`, `_s`, `_d`, `_days`, or a
  `days_since_` name) that rose by the status time elapsed, within the slack, did not move: `plan.days_since_advance`
  up 1/24 in an hour and `plan.list_age_h` up 1 in an hour are not news (the item's step 1 acceptance check). The time
  is the two points' own `observed_at` when both rows carry it, and one step of a value's decimal rounding (0.01 d =
  864 s, capped at half the time elapsed) is not movement.
- **a-clock-reset-is-news.** The same clock falling (a reset to 0), or rising by more or less than the time elapsed
  beyond the slack and one step of its own rounding, is news. (An unchanged value is not news, as before this page.)
- **a-banded-count-inside-its-band-is-not-news.** A metric whose route carries a `band` (`wrapup.debris_standing`)
  that flaps inside the band, even across its alarm line (0 to 3 and back, the alarm coming and going), is not news.
- **a-banded-count-leaving-its-band-is-news.** The same metric moving out of its band, or its reading going
  unmeasured, is news.
- **the-five-repeat-alarms-are-program-routes-with-a-runbook.** `steve.incident_unclaimed_min`,
  `accounts.lukas.runway`, `wrapup.debris_standing`, `maturation.idle_owed_max_min` and `disk.scratch_dirty_end` route
  `program` with a `runbook` line, a `band`, a `reader` and a `cause` (the item's step 2 acceptance check); their
  sibling metrics (`accounts.system.runway`, `steve.invalid_streak`, `disk.scratch_dirty_start`) still reach Operations.
- **in-band-opens-no-incident.** `step` opens no incident for an OPEN alarm on a banded program route whose reading is
  MEASURED inside its band.
- **out-of-band-opens-the-routes-incident.** The same alarm with its reading outside the band opens an incident of the
  route's `cause` for its `reader`, as a role route would.
- **an-unmeasured-reading-calls-the-agent.** A reading absent, not MEASURED, or not a number is never "in band":
  `program_answer` says `agent`, with the cause named.
- **a-program-answered-alarm-buys-no-alarm-run-and-is-noted-once.** In `decide_roles` an open alarm whose banded
  program route reads in band launches no Operations alarm run; the program writes the runbook line as one ledger note
  on the alarm's item (the role's own item when it has none), once per key while it stays open, and the key is not
  marked seen.
- **leaving-the-band-gets-its-run.** The same alarm, its reading out of band on a later tick, launches the alarm run
  at once.
