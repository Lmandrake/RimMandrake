# BOUNDARY: the incident clerk (a plan's trigger line, read by a program), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/incident.py` (`parse_trigger`, `trigger_state`, `clerk_trigger`, `clerk_news`,
`deep_read_at`, the clerk and deep-read passes in `step`, `ack`'s `trigger`), `rimflow ack --trigger` in
`src/RimMandrake/rimflow/cli.py`, the deep read's model in `src/RimMandrake/rimflow/dispatcher.py` (`incident_run`,
`incident_execute`) and `src/RimMandrake/rimflow/role_launch.py` (`job_model`, `launch_role`), and the policy key
`deep_read_local` in `src/RimMandrake/rimflow/alarm_routes.json`. Item: `RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED`,
written 2026-11-19, from the owner's card of 2026-11-19 ("Program follows open incidents": "A program re-reads each
open incident's numbers and calls the agent only when one crosses a stated line; one deep Opus run a day stays", owed:
"each incident plan needs a line a program can check") and
`D:\ClaudeWork\rimmandrake\conductor\operations_role_analysis_20261117.md` section 4 item 3 and section 5 option (d).
It builds on `design/specs/2026-11-19-incident-news-and-program-routes/boundary.md` (the news grading it keeps for a
plan with no trigger line). Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_incident_clerk.py`.

## ACCEPTS (the only inputs these readers are built for)

- **a-trigger-line.** The text of `rimflow ack <id> --plan "..." --trigger "<clause>[; <clause>...]"`. A clause is
  `<metric> <op> <number>` (`op` one of `< <= > >= == !=`; the metric is a `status.json` point key) or
  `after <YYYY-MM-DDTHH:MM[:SS]Z>` (a UTC time). Clauses are joined by `;` and the trigger is crossed when ANY clause
  is true. `ack` refuses a line that does not parse, naming the clause; an ack with no `--trigger` stores none, so a
  new plan never inherits the old plan's line.
- **an-open-incident-at-his-rung.** A folded `told.jsonl` incident at `OWNER_RUNG`, its `trigger` from its last run's
  ack (an auto-ack from an item action carries none), read beside the same tick's `status.json` and its freshness.
- **the-deep-read-time.** Policy `deep_read_local` (`"HH:MM"`, the dispatcher machine's local time); absent or null,
  there is no deep read.

## DOES NOT SURVIVE (not promised)

- **a-change-the-trigger-does-not-name.** While a plan's trigger line holds, a reading that moved, a plan rewritten,
  or an action on a named item is not news: the run that wrote the line said what matters. A cause only a model would
  see in those readings waits for the daily deep read. The card's stated cost: "less free re-reading".
- **a-metric-clause-between-revisits-that-cannot-be-read.** Between due revisits the clerk acts only on a CROSSED
  trigger; a blind clause calls the agent at the incident's next due revisit, not at once.
- **an-incident-below-his-rung.** The clerk reads triggers only at his rung, where revisits happen. Below it the ladder
  climbs on its own clock, and every climb is a rung change that buys its run.
- **a-deep-read-with-nothing-to-read.** With no open incident at his rung the deep read writes nothing and is tried
  again each tick of that day; an incident that reaches his rung later that day is read by it then.
- **a-deep-run-the-launcher-refuses.** The deep read's rows land when the ring is made; a run the launcher then holds
  or refuses is re-asked as the dispatcher re-asks any fresh run, and is not re-written as a second deep read.

## PROMISES (each one is owed a test of the same name)

- **a-trigger-line-is-parsed-or-refused.** `parse_trigger` returns one clause per `;` part for a metric comparison or
  an `after` time, and raises `ValueError` naming the part for anything else (empty text, an unknown operator, a
  non-number, a time not in UTC `Z` form); `ack` stores the parsed line's text as `trigger` and refuses a bad one.
- **a-held-trigger-writes-the-no-change-row-and-pushes-the-revisit.** An incident at his rung, due for a revisit,
  whose trigger line holds (no clause true, every metric clause MEASURED) writes one `revisit_quiet` row with
  `clerk: true` and a `still` text naming each clause's reading ("still X, no change"), re-arms its revisit a floor
  later, and rings no run, even when its readings moved.
- **a-crossed-trigger-launches-one-run.** A trigger clause true on a tick, due or not, revisits that incident once:
  one `revisited` row whose news names the crossed clause and its reading, one fresh Operations ring, and the trigger
  cleared with the plan, so the next tick launches nothing more.
- **a-rung-change-launches-one-run.** With its trigger holding, an incident whose rung moved since the last look (an
  `escalated` or `reopened` row) or that gained a metric is revisited with one run; one below his rung that climbs
  rings exactly one run for the climb.
- **a-trigger-that-cannot-be-read-calls-the-agent.** At a due revisit, a metric clause whose point is absent, not
  MEASURED or not a number, a stale status, or a stored line that does not parse, is never "held": the incident is
  revisited with the cause named.
- **a-plan-with-no-trigger-keeps-its-model-revisit-and-is-asked-for-one.** An incident whose plan has no trigger line
  is graded by `revisit_news` as before (moved readings buy a run); its `revisited` and `revisit_quiet` rows carry
  `trigger_owed: true`, and the run's ring asks for a `--trigger` line.
- **the-daily-deep-read-launches-once-a-day-on-opus.** From `deep_read_local` each local day, the first tick revisits
  every open untamed incident at his rung that is not recovering, as one batch of `deep` rings (`revisited` rows with
  `deep: true`), whatever their triggers say; a later tick that day adds none; the next day it comes again. The
  dispatcher asks that batch as one Operations run carrying `model: opus`, and `launch_role` launches it on Opus even
  when the role's `model_by_mode` would pick another model.
