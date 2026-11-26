# WB-pipeline-operations-20261126-152121

Home: pipeline:operations. Members: 1.

## Step A (done)

| member | class | act |
|---|---|---|
| `OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ` | done already | closed at e8c75ecf2d (fix 81d617a484, guard replay e8c75ecf2d) |

Evidence: the reopen at 2026-11-26T13:15Z read 1 end problem, `refused_gb 27.74 over 25`. Two clones' publish check
trees (`.git/rm-treecheck-*`) read as nested repos (23.3 GB). Commit 81d617a484 (`own_check_tree`,
`selftest_scratch_reap_checktree.py`) fixed this. The Archmagi `rm-scratch-reap` run that started at 07:00:23 PST ran
on dispatch a0845ecf5b, which holds 81d617a484. Its end at 2026-11-26T16:09:10Z
(`~/.local/state/rm-scratch-reap/sanity.json` on Archmagi, `prev_end`) reads `problems []` and `refused_gb 2.68`.

## Steps B and C

Nothing kept, so no check to write and no work to do.

The close gate wanted a class guard. `selftest_scratch_reap_checktree.py` got `--at <rev>` (e8c75ecf2d). It was
shown red at `--at 81d617a484^` (cases A and D) and green at HEAD. A second end with the fix, at 2026-11-26T18:12:30Z,
also reads `problems []`.

## Next

Nothing. The bundle is complete: 1 of 1 members closed.
