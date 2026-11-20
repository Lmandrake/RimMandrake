# RIMMANDRAKE_BATCH_SCRATCH_ARCHIVE_QUEUE_GROWS_HOURLY

## Finding (Operations, incident disk-20261115210535, measured 2026-11-19 16:40 PST)

The hourly scratch reaper (`src/RimMandrake/Utils/scratch_reap.py`, `rm-scratch-reap.service`) again archives tiny clones more slowly than they age out. Its deferred queue grows each run:

- Last three apply runs (journal of `rm-scratch-reap.service`; `~/.local/state/rm-scratch-reap/last_run.json`):
  - 2:03 PM PST: ARCHIVE 115, DELETE 35 deferred; wall 30m08s.
  - 3:01 PM PST: ARCHIVE 341, DELETE 41; wall 31m51s.
  - 4:01 PM PST: ARCHIVE 608, DELETE 51, `deferred` 659, `archived` 171; wall 30m07s (1802 s). `phase_s.apply` 1438.8 s, so about 8 s per row.
- Before 2 PM today every run ended clean in 2-24 min with ARCHIVE 0. The `lender_gone` commits (e1baaf325a, 86cced0192) landed at 5:30-5:45 AM, eight clean runs earlier, so they are not the trigger.
- 592 of the 608 ARCHIVE rows are clones. 568 of those are ~28-29 KB `~/.seat-tmp/BENCH/tmpXXXXXXXX` selftest clones, 24-25 h old. The rest are a few `/tmp/tmpX`, two `rf_cstage_*/repo` and one 271 MB `/tmp/designer-review.*/ported`.
- 1745 YOUNG rows wait behind them. Most are the same kind (`selftest_seat_restart_*/unpub_*/c`, 21-24 h old), so the queue keeps growing for about a day even if no more are made.
- `apply_slowest` lists only 28 KB clones: 224 s, 79 s, 31 s, 28 s, 25 s. `borrow_walks` n 3, total 379 s, max 203 s. So a few walks of the alternates chain take a quarter of the budget.
- End sanity reads `session_stale 97 over 60` and `659 row(s) deferred past the time budget`, so `disk.scratch_dirty_end` stays 2 and the incident cannot close. The disk itself has room (root 565 GB free; scratch 28.6 GB).

This is the same fault class as RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH. That item's fix 1 (archive throughput) did not hold against this burst.

## Fix (the fixer picks)

- Do not raise the 30 min budget. That only moves the queue; it is a looser limit.
- Choices:
  - Bundle a selftest's mkdtemp clones in one batched pass, not one per row.
  - Treat a clone under a selftest's own tmp root, whose only unpushed commits are the fixture's own, as a disposable fixture.
  - Make the selftest that makes them (`selftest_seat_restart*` and the `tmpXXXXXXXX` makers under `.seat-tmp/BENCH`) clean up its own clones.
  - Cap the time of one `lender_gone` alternates walk, or cache it per lender.
- Also find why one 28 KB clone takes 224 s (`apply_slowest`).

## Acceptance test

- Offline: a selftest that builds 200 tiny fixture clones of the `tmpXXXXXXXX` shape, past TTL, and requires one apply run to clear them all well inside the budget. It must fail on the current base.
- Live oracle: `last_run.json` `deferred` reads 0 and the ARCHIVE count falls across three consecutive apply runs. `disk.scratch_dirty_end` then reads 0.
