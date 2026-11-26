# BOUNDARY: the scratch reading is aged from when its row was written, Design Version 0.1.0

Code: `scratch_reading` in `src/RimMandrake/Utils/ops_watch.py` (the `disk.scratch_total_gb` and
`disk.scratch_refused_gb` points of the disk family), and the runs.jsonl row that `run` in
`src/RimMandrake/Utils/scratch_reap.py` writes. Item: `RIMMANDRAKE_SPEED_SCRATCH_REAP_APPLY_RUNS_PASS_TWO_HOURS`,
written Thu 2026-11-26. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_scratch_reap_row_age.py`.

## The danger the limits guard

- **The 3 h bound on the row's age.** It guards a dead or hung reaper. Such a reaper writes no new row, so its last
  reading freezes while the disk changes. The bound is unchanged by this page; what moved is the clock it reads.
- **Why the clock moved (measured 2026-11-24..26 on Archmagi).** The row is written at the END of a run, but the
  reader aged it from `ts`, the run's START. Runs grew to 1.5-2.3 h (journal `Consumed` lines of
  `rm-scratch-reap.service`), so a row read up to 2.3 h old the moment it landed, and the two points read UNMEASURED
  for part of every cycle. Runs then ended at most about 2.3 h apart, so a row aged from its write is never 3 h old
  while the reaper lives.

## ACCEPTS (the only inputs this is built for)

- **the-last-runs-jsonl-row.** The last line of `RM_SCRATCH_REAP_RUNS` (default
  `~/.local/state/rm-scratch-reap/runs.jsonl`): a JSON object with `ts`, `rows`, and, from this version, `end_epoch`.

## DOES NOT SURVIVE (not promised)

- **a-run-over-three-hours.** A live run that takes more than about 3 h after the last row was written still reads
  UNMEASURED until it writes its row. No run that long is on record.

## PROMISES (each one is owed a test of the same name)

- **the-row-carries-its-write-time.** An apply run of the reaper writes `end_epoch` on its runs.jsonl row, the time
  the row was written.
- **a-slow-live-reaper-reads-measured.** A row whose run started 3.5 h ago and that was written 20 min ago gives a
  MEASURED `disk.scratch_total_gb`.
- **a-dead-reaper-still-ages-out.** A row written more than 3 h ago reads UNMEASURED.
- **an-old-row-is-aged-by-its-start.** A row with no `end_epoch` is aged from `ts`, as before.
- **a-future-row-is-refused.** A row written more than 5 min in the future reads UNMEASURED.
