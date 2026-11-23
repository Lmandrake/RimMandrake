# BOUNDARY: the graph of tickets by hour on MATURATION_NOW, Design Version 0.1.0

Code: `src/RimMandrake/Utils/maturation_trend.py` (all of it) and its calls in `src/RimMandrake/Utils/maturation_now.py`
(`trend`, `build`, `phone_trend`). Tests: `src/RimMandrake/Utils/selftest_maturation_trend.py` (each promise below has a
test of its name). Item: `RIMMANDRAKE_REDRAW_NONMOD_PAGE_HALF_SLEEK_SUMMARY_NOT_LOG_BARF`. The owner, 2026-11-23: *"of
the tickets NOT held (due to staleness, old mods, etc), not many are waiting, being worked, and have been completed as a
function of hour for the past five days would be a great start. ... waiting(mod), waiting(non-mod), opened(mod),
opened(non-mod), closed(mod), closed(non-mod)"*.

## ACCEPTS

- **the-ledger.** The events of `model.read()`, folded by `model.replay` with its `observe` call; or nothing.
- **the-run-records.** The detached-run records (`item`, `at`, `ended`, `status`, `live_state`), or nothing.
- **the-hold-list.** `mod_owner_hold.json`, as it stands now. It is used for all five days.
- **the-mods.** The mods on the page, and every mod folder with an About.xml (`src/*/*/About/About.xml`).

## DOES NOT SURVIVE

- **a-hold-that-changed-in-the-window.** Today's hold list is applied to every hour, so a mod held or lifted inside the
  five days shows no step.
- **an-old-mod-named-in-other-words.** An old mod is known by its whole folder name in a ticket's id or title. A ticket
  that names it in other words counts as non-mod work.
- **an-event-written-late.** An event carries the time of its writer's clock. A clone that lands its events late moves
  an earlier hour on the next build.

## PROMISES

- **hours-of-five-days.** 120 whole clock hours and the hour in progress, each with its own reading.
- **stocks-and-flows-by-replay.** Waiting is read at the end of each hour; opened and closed count the tickets that
  became open (filed, spawned or reopened) or stopped being open (done, dropped, superseded) in that hour. With nothing
  stale or parked, waiting moves by exactly opened minus closed. An event after now is not counted.
- **left-out-tickets-are-named-and-counted.** A ticket is left out when it is on a mod he holds, on an old mod, for a
  later version, parked (a wait not come, or a block whose blocker is still open or that names none), or stale (not
  filed, taken up, run or given a check, wait or block in `STALE_DAYS`). The first that is true is its group. A note,
  a re-homing or a program's re-check does not make a ticket fresh. The page prints each group with its count, and how
  many opened and closed events fell on left-out tickets and are not drawn. A ticket filed and parked at once is opened.
- **mod-by-the-page-rule-and-unclassed-counted.** Mod or non-mod is `maturation_nonmod.classify`, the page's one rule.
  A ticket it cannot class is in no line, and is counted.
- **worked-is-run-or-lease.** A ticket is being worked at the end of an hour when a run was live on it or its lease was.
  A worked ticket does not wait. With no run records, being worked reads UNMEASURED.
- **replay-matches-the-ledger.** The open tickets at the end of the replay are the ledger's open tickets: waiting, worked,
  left out and not classed add up to them. A mismatch is counted and printed.
- **graph-is-one-line-with-six-series.** The section is one line of HTML (Typora) with one SVG: waiting in one panel, a
  thin panel for being worked, and one panel per class with opened above zero and closed below it, on one shared scale
  and one time axis. No mark lies off the graph. Same inputs, same graph.
- **four-answers-differ.** No ledger reads COULD NOT LOOK with the cause; a build that raises reads FAILED with the cause;
  neither draws a graph. A measured zero draws a graph that says 0. An unread run record reads UNMEASURED.

## LIMITS

- **120 hours**, his words ("the past five days").
- **7 days to stale (`STALE_DAYS`).** Danger: the old backlog hides the week's change. Evidence: on 2026-11-23 over 600
  of the 1,174 open non-mod tickets had no act in seven days.

## LIFE CYCLES

- **a page build:** `gather` reads the ledger and the run records once → `trend` folds the ledger a second time, hour by
  hour → `block` and `phone_trend` draw one list of primitives (`ops`).
