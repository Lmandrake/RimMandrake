# RIMMANDRAKE_IGNORE_SEAT_QUEUES_AND_MODSET_SNAPSHOTS

## spec

Measured 2026-11-16 08:13 PST: the seat clone /home/mandrake/rm/bench held 15 untracked rimflow queue projections
(`infrastructure/state/queue/CLAUDE_ARCHMAGI_OFFLINE1.md` ... one per runner seat, rendered on every claim; only
BENCH.md and FOUNDRY.md were ignored) and modset_builder's ModsConfig before-tier snapshots (copies of the live mod
list; 31 tracked, 2 untracked, 1 tracked one rewritten). Every clone that renders a queue or swaps a tier went dirty.
Fix: ignore `infrastructure/state/queue/*.md` except the hand-written HUMAN.md, CHECK_CLOSED.md, DECIDE_ARCHIVE.md;
ignore `deployed/config/ModsConfig.before-tier-*.xml` and `ModsConfig.swap-active*.json`; untrack the 32 tracked ones
(the bench copies are put back on disk, ignored, so modset_builder's restore still finds them).

## verify

`python3 src/RimMandrake/Utils/run_selftests.py --only selftest_generated_paths_ignored` (1 test). Watched FAIL on
the base (4 paths not ignored, 32 tracked derived files), PASS after.

## criteria

- Every rendered queue view and every before-tier snapshot is ignored and untracked; hand-written queue files are not.
- selftest_generated_paths_ignored red on the base, green after.
