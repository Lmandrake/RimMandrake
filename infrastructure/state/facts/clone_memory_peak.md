# What one relentless clone costs in memory, and who holds it

Item `RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK`. MEASURED 2026-11-03 on Archmagi (36 GB WSL2, 14 cores), store
`/home/mandrake/rm/store.git` (21 GB), worktree of a full checkout ~3.8 GB. Instrument:
`python3 src/RimMandrake/Utils/clone_mem_probe.py --runs N` — one clone made exactly as `relentless.py` makes it
(`scratch_clone.py clone ... --checkout --fetch`, `RM_SEAT=clones`) inside its own systemd user scope, so the cgroup's
`memory.peak` is that clone alone: the same counter systemd prints as the tick unit's "memory peak".

| run | cgroup memory.peak | anon at peak | page cache (file) at peak | largest anon process | host MemAvailable dip |
|---|---|---|---|---|---|
| 1 | 2.00 GB | 0.22 GB | 1.64 GB (1.34 GB dirty) | `git read-tree` | not sampled |
| 2 | 3.11 GB | 0.22 GB | 2.71 GB (88 %) | `git read-tree`, 0.21 GB RssAnon | 0.53 GB |
| 3 | 2.34 GB | 0.15 GB | 2.07 GB (89 %) | `git read-tree`, 0.21 GB RssAnon | 0.45 GB |

Records: `D:\ClaudeWork\rimmandrake\clone_mem_probe\run-*.json` (scratch; each holds a 0.5 s timeline).

## The answer

- **git holds it, not `scratch_clone.py`.** `scratch_clone.py` peaks at ~24 MB. The peak is `git read-tree -mu HEAD`,
  the checkout, from t≈2 s to the end of the clone (~13 s wall).
- **It is page cache, not process memory: 82–89 % of the peak is `file`.** read-tree writes the ~3.8 GB worktree;
  the written pages (mostly dirty at the peak) are charged to the cgroup that wrote them. Anon is ~0.2 GB.
- `git read-tree` shows ~2.8 GB **VmRSS**, of which 0.21 GB is RssAnon: the rest is the store's packfiles mmapped,
  shared and reclaimable. Reading VmRSS calls it a 2.8 GB process; it is not.
- **The host feels ~0.5 GB, not 2–3 GB:** MemAvailable fell 0.45–0.53 GB during a clone and was 0.21–0.37 GB below
  its start at the end, because clean page cache counts as available.
- A tick's "memory peak" is the high-water mark of the whole `rm-relentless.service` run, and page cache stays charged
  to it until reclaimed, so a tick that makes two clones (builder and checker, or a re-made clone) reads 4–5 GB with
  under 0.5 GB of anon. Workers are their own systemd units and are not in that number. The tick journal over
  2026-10-31 to 2026-11-03 shows peaks up to 10.9 GB (`journalctl --user -u rm-relentless.service | grep "memory peak"`);
  those were not taken apart here.

## What this means for the stop lines

`min_mem_available_gb` (6) and the 3 GB host stop line read MemAvailable, which already treats this page cache as
available. Budgeting a clone at 4–5 GB against them overcounts it several times over; ~0.5 GB of MemAvailable per
concurrent clone is the measured figure. Recheck: `clone_mem_probe.py --runs 1 --check` exits 1 when the peak is
no longer mostly page cache or a python process becomes the largest anon holder.
