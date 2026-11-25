# BOUNDARY: the owed view shows the waits that name the Conductor, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/owed.py` (`named_waits`, `banner`, `view`).
Tests: `src/RimMandrake/rimflow/selftest_owed_view.py` (each promise below has a test of its name). Acceptance of the
whole owed view: `src/RimMandrake/rimflow/acceptance/owed_view_accept.py`.
Item: `RIMMANDRAKE_SHOW_CONDUCTOR_THE_WAITS_THAT_NAME_IT_TWENTY_TWO_UNSEEN`, written 2026-11-24.

Why. A detached run that finishes its part writes a `LEFT OPEN:` note and a dated wait whose reason is "the Conductor
reads, rules, shows or releases". The Workshop Pipeline reads a wait as Waiting. The no-home count reads it as a need that
has a home. The owed view read only items of kind `owed`. So no list asked the Conductor. Measured 2026-11-24: 21 open
items of that shape, seven of them with a date that had passed, and 6 of the 15 items that the owner's question of
2026-11-23 ("worked but didn't get closed") named.

## ACCEPTS

- **the-replayed-ledger.** `named_waits(world, seat, now)`: items with `owner`, `open`, `kind`, `wait_until`,
  `wait_reason`, `title`.

## DOES NOT SURVIVE

- **a-next-act-written-only-in-a-note.** An item whose note says that the Conductor acts next, with no dated wait, is not
  in this block.
- **a-wait-that-only-mentions-the-conductor.** A reason that names the Conductor and asks another party is shown too.

## PROMISES

- **a-wait-that-names-the-conductor-is-in-the-view.** `view` has a block `YOURS BY A WAIT (<k>)` with one line per item:
  its date, id, title and reason, the soonest date first. The first line of the view ends with the count.
- **only-an-open-wait-of-this-seat-that-names-the-conductor.** An item of another seat, a closed item, an item with no
  wait or no reason, a reason that does not name the Conductor, an owed item and a standing notice are not in the block.
- **a-passed-date-is-said.** A line whose date has passed says `PASSED <date>`.
- **the-first-line-says-the-count-even-when-the-lines-are-cut.** The 40-line cap can cut the block; the first line still
  says how many waits name the Conductor. With none, the first line is as it was.

## LIFE CYCLES

- **a wake or a prompt:** `rimflow queue CONDUCTOR --owed` (or the per-prompt notice) → `banner` and `view` → `named_waits`.

Later lists beside this page: `polish.md` (none yet).
