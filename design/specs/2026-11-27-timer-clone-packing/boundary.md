# BOUNDARY: git packs the timer clones in its own unit, never inside a timer's run, Design Version 0.1.0

Code: `src/RimMandrake/Utils/clone_pack.py`, run by `rm-clone-pack.timer` (`src/RimMandrake/Utils/systemd/`), and the
call of `clone_pack.hold` at the top of `sync_clone` in `src/RimMandrake/rimflow/maturation_dispatch.py`. Tests:
`src/RimMandrake/Utils/selftest_clone_pack.py` (real git in temporary repos). Item:
`RIMMANDRAKE_UNHOOK_GIT_PACKING_FROM_TICK_TOOK_13_MIN`, written 2026-11-27.

## The failure

- The Maturation Pipeline tick (`rm-maturation-dispatch.service`, `MemoryMax=1G`) runs `git fetch` (`seat_sync.py`)
  and `git commit` (`land.sh`) in `/home/mandrake/rm/dispatch`. Each of those starts git's automatic maintenance when
  the clone has many loose objects or packs: `git maintenance run --auto`, then `git gc --auto`, then `git repack`,
  then `git pack-objects --all --reflog`.
- On 2026-11-27 the clone held 8795 loose objects (4.4 GB) and 41 packs (11.6 GB). The packing ran inside the tick's
  1 GB unit. The tick that ended at 12:47:08 AM PST took 13 min 24 s and swapped 7.1 GB; the next took 4 min 31 s and
  swapped 6.5 GB. Before, a tick took 0.5 to 2.6 min.
- When the tick's main process ends, systemd kills what is left in the unit, the packing included. Each kill leaves a
  `tmp_pack_*` or `tmp_obj_*` file, and the next tick starts the packing again. The clone held six such files, dated
  2026-11-15 to 2026-11-24.
- The same failure hit `/home/mandrake/rm/pulse-deploy` on 2026-11-16 (284 `tmp_pack_*` files, 196.7 GiB; lesson
  `infrastructure/state/lessons/20261119T084833Z-BENCH-git-index-lock-file-exists-refusal.md`). That fix was a hand
  `git config`, and on 2026-11-27 that clone had the setting unset again. `/home/mandrake/rm/bench` had `gc.auto=0`
  by hand and nothing packed it: 125648 loose objects (36 GB) and 669 packs.

## The design

- **Hold.** `hold(root)` writes `gc.auto=0` and `maintenance.auto=false` into the clone's own `.git/config`. Then no
  git command in that clone starts automatic packing, in any unit. `sync_clone` calls `hold` first on each applying
  tick, before its fetch, so a dispatch clone made again has the hold before the tick's first fetch. Each run of
  `rm-clone-pack` also holds every timer clone, so a clone that another tool made again has the hold within an hour.
  A clone that git made new holds one pack, and git starts its own packing only past 50 packs or about 6700 loose
  objects, so the hour leaves no gap that a timer can reach.
- **Timer clones.** `timer_clones()` reads every unit file in `src/RimMandrake/Utils/systemd/` and in
  `~/.config/systemd/user/`. Each path under `/home/mandrake/rm/` in a `WorkingDirectory=` or `ExecStart*=` line that
  lies in a git work tree names that work tree. A bare repository (`mirror.git`, `store.git`) is never named: those
  have their own rules (`mirror.py`, `scratch_clone.py` `STORE_CONFIG`).
- **Pack.** `rm-clone-pack.service` runs `clone_pack.py run --apply` once an hour, in its own unit. For each timer
  clone it first deletes the dead temporary files (below). Then it packs the clone at about the point where git itself
  would have packed it: 6700 or more loose objects, or 50 or more packs (git's own `gc.auto` and `gc.autoPackLimit`
  defaults; git 2.53 packs at 51 packs, and it estimates the loose count from `objects/17`). The pack
  is `git repack -d -q --geometric=2` with `pack.threads=4` and `pack.windowMemory=256m`: it packs the loose objects
  and rolls the small packs into one, and it leaves the large pack as it is. It prunes nothing: an object that the
  clone holds stays readable.
- **Dead temporary files.** A `tmp_pack_*` in `objects/pack/` or a `tmp_obj_*` in `objects/??/` that nobody wrote for
  6 hours is the leftover of a killed git process, and `run` deletes it. A git process that writes such a file writes
  it without a pause, so a file that has not changed for 6 hours has no writer.
- **Reading.** Each `run` writes `reading.json` in `$RM_CLONE_PACK_STATE` (default
  `~/.local/state/rimmandrake/clone_pack/`): for each clone, the hold, the counts before and after, the files deleted,
  whether it packed, the seconds it took, and any failure. The command exits 1 when a clone failed. The other clones
  are still done.

Offline simulation: yes. The selftest runs the real code on real temporary git repos with a fake clock for the age of
the temporary files and lowered pack thresholds; nothing in the design needs the live machine but the units.

## ACCEPTS (the only inputs this is built for)

- **non-bare-clones-under-rm.** Git work trees under `/home/mandrake/rm/` that a unit file names.
- **git-2.53.** `--geometric` needs git 2.33 or later.

## DOES NOT SURVIVE (not promised)

- **a-clone-named-only-by-a-script.** A clone that no unit file names, but that a timer's code reaches (a path inside
  a Python file), is not held or packed. Its own automatic packing still runs, inside whatever unit runs git there.
- **a-hand-unset.** Someone who unsets `gc.auto` by hand in a clone that the tick does not sync gets packing inside
  timers again for up to one hour.

## PROMISES (each one is owed a test of the same name)

- **hold-stops-auto-packing.** After `hold`, the clone's own config has `gc.auto=0` and `maintenance.auto=false`, and
  `git maintenance run --auto` and `git gc --auto` on a clone with 51 packs pack nothing. Before `hold`, the same
  commands repack them.
- **timer-clones-from-unit-files.** A `WorkingDirectory=` or `ExecStart=` path that lies in a work tree names that
  work tree once. A bare repository, a path that does not exist and a path outside the root are not named.
- **dead-temp-files-go-live-ones-stay.** `run` deletes a `tmp_pack_*` and a `tmp_obj_*` older than 6 hours, and keeps
  one that is younger, and keeps every real pack.
- **pack-when-git-would-have.** `run` packs a clone over the loose-object or pack-count threshold, leaves a clone
  under both thresholds unpacked, and a packed clone still reads its whole history (`git fsck --connectivity-only`).
- **one-failure-does-not-stop-the-rest.** A clone that git cannot read is reported failed in the reading, the other
  clones are still held and packed, and the command exits 1.

The tick's side, that `sync_clone` holds before it fetches, is the promise `sync-clone-holds-before-it-fetches` of
`design/specs/2026-11-26-tick-clone-sync/boundary.md`.

## LIMITS

- `PACK_S` (9000 s per clone) is a hang guard: 10 times the longest pack, bench's first (765 s).
- `TimeoutStartSec` of `rm-clone-pack.service` is a hang guard: a hung git holds the unit, and systemd starts no
  second run, so no clone is packed again. Evidence and size are written beside it in the unit file.
- No `MemoryMax`: the first run peaked at 15.8 G, page cache included (anon about 1.7 G, sampled mid-pack), with
  373 M of swap (2026-11-27). Ten times that is more than the machine. The memory of the delta search is set by
  `pack.windowMemory` and `pack.threads`, which end no work.
- The 6-hour age of a dead temporary file ends no work; its danger is written above (Dead temporary files).

## PROOF

- 2026-11-27, `git repack -d -q --geometric=2` of `/home/mandrake/rm/dispatch`, in its own transient unit, by hand:
  2 min 52 s, 5 min 32 s CPU, memory peak 5 G (swap 78.6 M). Loose objects 8906 (4.22 GiB) to 66 (61 MiB); packs 41
  (11.10 GiB) to 3 (10.27 GiB); prune-packable 34 to 0.
- 2026-11-27 1:07 to 1:28 AM PST, `clone_pack.py run --apply` in its own transient unit, before the timer existed:
  20 min 31 s, 52 min 47 s CPU, peak 15.8 G with page cache, swap 373 M, nothing failed. bench: 125769 loose objects
  (34.3 GiB) and 670 packs (15.7 GiB) to 83 loose and 4 packs (10.25 GiB), in 765 s, one dead `tmp_pack_*` deleted.
  pulse-deploy: 52231 loose (18.0 GiB) and 525 packs (15.6 GiB) to 25 loose and 3 packs (10.09 GiB), in 463 s, hold
  written. roles/artpiped: hold written, under both thresholds. dispatch: already held and packed.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
