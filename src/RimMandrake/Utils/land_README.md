# land.sh - publish one commit (or explicit paths) by plumbing, then realign the clone

Installed path `/home/mandrake/.seat-tmp/land.sh` is a one-line wrapper that execs this file (the bench clone's copy).

- `land.sh <sha> <path>...` replays that ONE commit onto origin/main. Every path the commit changes must be
  (or sit under) a listed path. Refuses: no sha, no paths, merge/root commits, a sha already an ancestor
  of origin/main or patch-equivalent to one (git cherry), conflicts.
- `land.sh -m "<msg>" <path>...` builds the commit itself from the working-tree content of the paths in a
  TEMP index seeded from origin/main - the clone's HEAD and index are never read.
- `LAND_REPO` defaults to the clone the cwd is in (`git rev-parse --show-toplevel`); outside a clone it refuses.
- After the push it records the new origin/main and runs `seat_sync.py --no-fetch`: main moves to origin/main with
  `git reset --keep` only when every local commit is already upstream; otherwise the reason goes to stderr and the
  clone is left as is (`./sync` later). `LAND_SYNC=0` skips it. stdout is exactly `PUBLISHED <sha>`.
- Never stashes, never --hard. Push is fast-forward only. Selftest: `selftest_land.py`.
