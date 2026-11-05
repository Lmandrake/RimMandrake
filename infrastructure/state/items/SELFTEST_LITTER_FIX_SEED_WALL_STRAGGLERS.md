## scope
Re-scoped 2026-11-05 (gen 3, per the attributed CONTRACT diagnosis rm-relentless-help-8c4b425c6a-g1-h1):
this item covers ONLY the seeds/wall litter makers, `selftest_relentless_seeds.py` and
`selftest_relentless_wall.py`, and the `seeddest*` / `seedrepo*` / `wallsha256*` shapes in `legacy_litter`.

The title's "(and an sbxd* maker)" clause has MOVED to `SBXD_FARMS_HUNT_MAKER_NOBODY_ADMITS`:
`~/.seat-tmp/BENCH/sbxd0..7` are symlink farms into the bench clone (`.git` a symlink to bench's)
with no maker in this repo, Lodestar, Machinist or git history, so no change here can make that
maker clean up; scratch_reap is right to refuse them until their maker is found.

## done when
- `python3 src/RimMandrake/Utils/run_selftests.py --only selftest_scratch_reap_litter,selftest_relentless_seeds,selftest_relentless_wall` is GREEN:
  seeds and wall runs, clean and SIGTERM-killed, leave nothing in their TMPDIR (both use
  `selftest_own_dirs.own_dir_for_run`), and `legacy_litter` finds old seedrepo/seeddest/wallsha256
  fixtures by exact shape and fixture git identity while keeping look-alikes.
- sbxd* is not an obligation of this item (see `SBXD_FARMS_HUNT_MAKER_NOBODY_ADMITS`).
