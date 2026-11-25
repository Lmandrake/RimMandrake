# BOUNDARY: the clone pool's admission and reuse, Design Version 0.1.0

Code: `pool_admit`, `pool_reading`, `pool_reuse` and `shed` in `src/RimMandrake/Utils/scratch_clone.py`. Item:
`RIMMANDRAKE_RESIZE_CLONE_POOL_CAP_CLONES_GREW_TO_FOURTEEN_GB`, written 2026-11-22. Each promise has a test of its name
in `src/RimMandrake/Utils/selftest_pool_floor.py`.

## The danger the limits guard

- **The disk line.** The danger is a full root disk (`/`, the WSL ext4 disk). On 2026-11-22 its virtual size was
  1007 GB and its file `E:\WSL\Ubuntu\ext4.vhdx` was on a drive with 2965 GB free, so `/` itself is the first thing
  to fill. A new pool clone is refused when the free space on the pool's disk, less the largest clone in the pool,
  would be under the floor. The floor is the `DISK_LOW` line: `ops.disk_brake_free_gb` in
  `src/RimMandrake/Utils/slot_rules.json` (210 GB, one worst day of scratch growth, 207 GB measured 2026-10-26). The
  slot allocator's disk brake reads the same key. Nothing else holds the number.
- **The count line.** 16 clones (the owner's card of 2026-11-02, "8 workers, 16 clones / 70 GB"). It guards clones
  that multiply with nobody to watch them (owner, 2026-10-31: "They seem to propagate prolifically"). The disk line
  does not guard that danger, so the count line stays.
- **The size age (`SIZE_MAX_AGE_S`, 1 h, and `SIZE_WALKS_PER_PASS`, 4).** Only ops_watch's disk sense uses them
  (`pool_reading(cached_sizes=True)`). They guard a clone that grew since its last walk. Free space on `/` is read live
  on every pass, so a stale size moves only the floor margin's "largest clone" term, never the free-space reading. The
  walk of every clone took 37.9 s in series (13 clones, load 29, 2026-11-22), past the sense phase's 15 s kill
  (`RIMMANDRAKE_UNBLIND_OPS_DISK_FAMILY_TWENTY_OVERRUNS_STRAIGHT`).
- **Why the old 80 GB line went.** It was a fixed pool size. On 2026-11-22 it refused a launch at 83.55 GB with 433
  GB free on `/`. A pool size does not measure free disk, and it refused work while the disk was safe.

## Why a clone grew from 4.5 GB to 16 GB (measured 2026-11-22)

- A fresh clone is 4.5 GB (4.3 GB work tree, 0.2 GB of its own objects). The large clones had all been reused.
- `pool_reuse` renamed an idle clone and kept every ignored file. The largest load was `Transient/modcheck/pyrelands/
  sites/saves_backup_1`: a copy of the whole Saves folder (585 `.rws`, 6 to 7 GB) that `Pyrelands/northstar_site.py`
  wrote into the clone. Every later item that got that clone carried it.
- Each ledger write adds a 5 MB loose blob of the 17 MB seat shard. Clones held 1.0 to 1.6 GB of loose objects, most
  of them also in a pack.
- `./publish` keeps one full checkout per clone for its checks (`.git/rm-treecheck-kept`, 3.4 to 4.6 GB) and reuses it
  (`design/specs/2026-11-25-treecheck-kept-tree/boundary.md`). A random-named one (`.git/rm-treecheck-<random>`) is made
  only beside it, and a publish killed with SIGKILL leaves that one.

## ACCEPTS (the only inputs this is built for)

- **a-pool-root.** A directory of clones, each a git work tree (`<name>/.git`).
- **slot-rules.** `slot_rules.json` with a number at `disk_brake_free_gb`, or `RM_POOL_FLOOR_GB` set.

## DOES NOT SURVIVE (not promised)

- **a-burst-of-launches.** Several launches that pass the check in the same second each see the same free space. The
  floor is 210 GB, so a burst of 16 clones of 16 GB still leaves free space.
- **growth-outside-the-pool.** The floor refuses new clones. It does not stop a clone, a build or a game that is
  already writing.

## PROMISES (each one is owed a test of the same name)

- **a-pool-of-normal-clones-with-free-disk-is-admitted.** 12 clones of 10 GB with 451 GB free on the disk: a new clone
  is admitted.
- **a-near-full-disk-refuses-a-new-clone.** Free space less the largest clone under the floor: the clone is refused,
  and the refusal names the free space, the floor and the key that holds the floor.
- **the-clone-count-limit-still-refuses.** 16 clones: a new clone is refused, whatever the free space.
- **the-floor-is-the-disk-low-line.** The floor is `ops.disk_brake_free_gb` in `slot_rules.json`, and that value equals
  the `DISK_LOW` alarm line on `disk.root_free_gb` in `ops_watch_rules.json`.
- **an-unreadable-floor-refuses-by-name.** When the floor cannot be read, a new clone is refused, and the refusal names
  the cause. It never falls back to a number.
- **a-reading-under-the-floor-is-a-breach.** `pool_reading` gives the free space, the floor and the margin; a margin
  under zero counts one breach, which `disk.pool_breach` reads.
- **a-reused-clone-sheds-what-the-last-run-left.** `shed` on a clone removes every ignored and untracked file, every
  random-named `.git/rm-treecheck-*` folder and every loose object that a pack holds. A tracked file, a commit and the
  kept check tree (`.git/rm-treecheck-kept`, which the next run's publish makes exact before use) stay.
- **pool-reuse-sheds-the-clone.** `pool_reuse` calls `shed` on the clone it gives.
- **the-sense-reading-walks-few-clones-a-pass.** `pool_reading(cached_sizes=True)` walks each clone with no size on
  record, each size older than `SIZE_MAX_AGE_S`, and the `SIZE_WALKS_PER_PASS` oldest of the rest. It uses no size older
  than `SIZE_MAX_AGE_S`. The count, the free space and the git readings stay live. Every other caller walks every clone.

Later lists beside this page: `polish.md`.
