# RIMMANDRAKE_RETAIN_SAVES_BACKUPS_NOTHING_REAPS_THEM

## spec

Filed by the 2026-11-15 cleanup pass (owner: "Let's make sure not to leave trash piling up. Protect canonical files of
course."). Evidence dir: `D:\ClaudeWork\rimmandrake\logs\cleanup_20261115\` (plan.tsv, deleted.tsv, result.md).

Retention that already runs: `rm-scratch-reap.timer` (hourly, `scratch_reap.py --apply`: clones and session dirs under
rm/scratch, ~/.seat-tmp, /tmp) and `rm-scratch-pressure.timer` (10 min). relentless_disk reaps boxes and done bundles.
Nothing else is reaped. The cleanup was done by hand with the existing tools. These six areas have no retention:

1. **RimWorld Saves folder.** `saves_prune.py` exists but nothing schedules it. Measured before the pass: 448 files,
   6.61 GB. 108 saves (1.15 GB) were from the last 7 days, 222 (3.28 GB) from the last 14 days and 370 (5.25 GB) from the
   last 30 days, so growth is about 160-230 MB a day. The pass pruned 110 (2.06 GB).
2. **Full Saves copies under `D:\ClaudeWork\backups`.** There are five 6.2-6.4 GB copies (Saves_20261023T0356,
   saves_20261113_evening, saves_20261114_htdoor, saves_pre_graffiti_walk_20261114, rimworld_saves_pre_pyre_visit1_20261115),
   plus saves_pre_cleanup_20261115 from this pass, about 38 GB in all. Four of the copies are from the last three days.
   Owner ruling 2026-10-18: a Saves backup lives only until its operation is verified. Nothing applies that ruling.
3. **`scratch/save_keepers`** (save_guard's content-addressed store) holds 9 GB and has no pruning.
   **`D:\ClaudeWork\backups\leftovers`** (the §2.2 archive) holds 5.4 GB and has no expiry.
4. **Transient/ expiry.** No tool expires unpinned Transient files. bench Transient held 9.25 GB in 40,103 files. The pass
   deleted 800 files older than 14 days that nothing names (408 MB). Most of the rest is under 14 days, art, or a sheet hub.
5. **Showing_ review saves.** `relentless_showing.py` writes `Showing_<ITEM>.rws` but never adds it to
   `infrastructure/state/saves_awaiting_review.txt`, so saves_prune cannot see that the save belongs to an open item. The
   pass added four by hand.

6. **`D:\ClaudeWork\rimmandrake\build` and `scratch`.** The pass deleted 151 winbuild stage caches whose newest dir was
   older than 14 days, about 10.1 GB. These include orphan `selftest_<csproj>_<clone hash>` stages from deleted clones.
   It also deleted the runtime subdirs (.sandbox-bin, cache, plugins) of 40 codex homes older than 14 days, at about
   410 MB each and 16.5 GB in all, plus 389 old debris and screenshot entries (2.3 GB). scratch_reap sees none of
   these: they are not clones or session dirs.

Also listed, all under 14 days: `~/.seat-tmp/BENCH/tmp.9az1Q6gedM` (2.7 GB, 11-03) and two more `tmp.*` repo exports from
11-05. These are mktemp trees, not clones, so scratch_reap never looks at them. Every non-pyc blob in them is already in git.

Scope (Relentless freeze: no new timer was asked for by this pass; decide whether to extend an existing timer's run or
schedule an existing tool): wire saves_prune and a backups/Transient age sweep into the existing reap path, and make
relentless_showing append its save to saves_awaiting_review.txt (removing it when the item closes).

Acceptance test: `python3 src/RimMandrake/Utils/saves_prune.py` dry run shows no PRUNE row older than 8 days, the run
being a day after the scheduled sweep fired. `systemctl --user list-timers` shows the sweep inside an existing unit.
