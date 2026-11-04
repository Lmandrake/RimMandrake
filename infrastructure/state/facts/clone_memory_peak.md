# What one relentless clone costs in memory, and who holds it

Item `RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK`. MEASURED 2026-11-03 on Archmagi (36 GB WSL2, 14 cores), store
`/home/mandrake/rm/store.git` (21 GB), worktree of a full checkout ~3.8 GB. Instrument:
`python3 src/RimMandrake/Utils/clone_mem_probe.py --runs N` — one clone made exactly as `relentless.py` makes it
(`scratch_clone.py clone ... --checkout --fetch`, `RM_SEAT=clones`) inside its own systemd user scope, so the cgroup's
`memory.peak` is that clone alone: the same counter systemd prints as the tick unit's "memory peak".

| run | store | cgroup memory.peak | anon at peak | page cache (file) at peak | largest anon process (RssAnon) | host MemAvailable dip |
|---|---|---|---|---|---|---|
| 1 | live | 2.00 GB | 0.22 GB | 1.64 GB (1.34 GB dirty) | `git read-tree` (this run read VmRSS, 2.98 GB; see below) | not sampled |
| 2 | live | 3.11 GB | 0.22 GB | 2.71 GB (88 %) | `git read-tree`, 0.21 GB | 0.53 GB |
| 3 | live | 2.34 GB | 0.15 GB | 2.07 GB (89 %) | `git read-tree`, 0.21 GB | 0.45 GB |
| 4 | live | 2.32 GB | 0.22 GB | 1.95 GB (84 %) | `git read-tree`, 0.21 GB | 0.38 GB |
| 5 | private | 4.50 GB | 0.17 GB | 4.20 GB (93 %) | `git read-tree`, 0.14 GB | 0.85 GB |
| 6 | live | 3.92 GB | 0.22 GB | 3.53 GB (90 %) | `git read-tree`, 0.20 GB | 0.13 GB |
| 7 | live | 2.60 GB | 0.22 GB | 2.24 GB (86 %) | `git read-tree`, 0.21 GB | 1.06 GB |
| 8 | live | 0.98 GB | 0.16 GB | 0.73 GB (75 %) | `git read-tree`, 0.21 GB | 0.79 GB |

Runs 1–4 2026-11-03 ~20:51, runs 5–8 ~21:06–21:10 (local). "private" = a store seeded outside the scope from the checkout's
HEAD tree (the probe's fallback when the live store is unreadable); the checkout it measures is the same.
Records: `D:\ClaudeWork\rimmandrake\clone_mem_probe\run-*.json` (scratch; each holds a 0.5 s timeline).

## The answer

- **git holds it, not `scratch_clone.py`.** `scratch_clone.py` peaks at ~24 MB. The peak is `git read-tree -mu HEAD`,
  the checkout, from t≈2 s to the end of the clone (~13 s wall).
- **It is page cache, not process memory: 75–93 % of the peak is `file`.** read-tree writes the ~3.8 GB worktree;
  the written pages (mostly dirty at the peak) are charged to the cgroup that wrote them. Anon is ~0.2 GB.
- `git read-tree` shows ~2.8 GB **VmRSS**, of which 0.21 GB is RssAnon: the rest is the store's packfiles mmapped,
  shared and reclaimable. Reading VmRSS calls it a 2.8 GB process; it is not.
- **The host feels 0.1–1.1 GB, not 2–4.5 GB:** MemAvailable's lowest point during a clone was 0.13–1.06 GB below its
  start, because clean page cache counts as available.
- **One clone alone reaches 4–4.5 GB of cgroup peak** (runs 5, 6): how much of the written worktree is still charged
  at the high-water mark varies run to run (0.98–4.5 GB over 8 runs). So a tick's 4–5 GB "memory peak" (the high-water
  mark of the whole `rm-relentless.service` run) is within what ONE clone's page cache produces; it does not need two
  clones. Workers are their own systemd units and are not in that number. UNMEASURED: the tick journal's larger peaks
  over 2026-10-31 to 2026-11-03, up to 10.9 GB (`journalctl --user -u rm-relentless.service | grep "memory peak"`),
  were not taken apart.

## What this means for the stop lines

`min_mem_available_gb` (6) and the 3 GB host stop line read MemAvailable, which already treats this page cache as
available. Budgeting a clone at 4–5 GB against them overcounts it several times over; ~0.5 GB of MemAvailable per
concurrent clone is the measured figure (worst seen 1.06 GB). Recheck: `clone_mem_probe.py --runs 1 --check` exits 0
while >= 60 % of the peak is page cache and a git process is the largest anon holder, 1 when either stops being true,
2 when it could not measure (no user scope, clone failed, or too few samples / too small a peak to have seen the
checkout). It needs neither the live store, GitHub nor Lodestar: it falls back to a private store and a TMPDIR record
dir and prints which it used.
