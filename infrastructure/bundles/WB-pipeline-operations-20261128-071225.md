# WB-pipeline-operations-20261128-071225

Home: pipeline:operations. Members: 1.

## Step A (done)

| member | class | act |
|---|---|---|
| `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ` | keep | fixed and closed at 1d01fa608b |

Evidence: the reopen at 2026-11-28T07:04Z read 1 end problem. The Archmagi `rm-scratch-reap` run of 04:00Z ended
`ok False` with one failure, `/home/mandrake/.seat-tmp/BENCH/tmp.kzi5Lh4TMd/tmp1otmqzap: [Errno 12] Cannot allocate
memory`, in `preserve()` (`~/.local/state/rm-scratch-reap/last_run.json`, `alarms.log`). drvfs answers ENOMEM under load.
The next run archived the same dir at 07:12Z. The failed attempt left `.incoming-6_xh5zj6` in
`/mnt/d/ClaudeWork/backups/leftovers/2026-11-27/scratch_expiry/`. The same preserve ENOMEM is in `alarms.log` on
2026-11-02. Kept by test 1: the failure happened twice, and each reopen launches an agent run.

## Step B (done)

Outcome check: `cmd:python3 src/RimMandrake/Utils/selftest_scratch_reap_preserve_enomem.py --at origin/main`.

## Step C (done)

- Fix 1d01fa608b: `preserve_retrying` retries ENOMEM after 5 s and 30 s. `preserve` removes its `.incoming-` dir when
  any step before the final rename raises. Page: `design/specs/2026-11-28-reap-preserve-transient/boundary.md`.
- Guard `selftest_scratch_reap_preserve_enomem.py`: red at `--at 1d01fa608b^` (5 fails), green at HEAD. The 6 reap
  selftests that the change touches are GREEN.
- `.incoming-6_xh5zj6` was removed by hand on Archmagi. Its dir is archived whole; 0 `.incoming-` dirs are left.
- Fresh reader: `RIMMANDRAKE_READ_FIX_1D01FA608B_WITH_FRESH_EYES`.
- The close's live line held after `rm-scratch-reap.timer` fired at 2026-11-28 00:03:22 PST.

## Next

Nothing. The bundle is complete: 1 of 1 members closed.
