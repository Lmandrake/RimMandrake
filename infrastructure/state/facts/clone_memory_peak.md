> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# What one relentless clone costs in memory, and who holds it

Item `RELENTLESS_TICK_MEASURE_CLONE_MEMORY_PEAK`. MEASURED 2026-11-03 on Archmagi (36 GB WSL2, 14 cores).

- The store is `/home/mandrake/rm/store.git` (21 GB). The worktree of a full checkout is ~3.8 GB.
- The instrument is `python3 src/RimMandrake/Utils/clone_mem_probe.py --runs N`.
- The probe makes one clone exactly as `relentless.py` makes it (`scratch_clone.py clone ... --checkout --fetch`,
  `RM_SEAT=clones`).
- The clone runs inside its own systemd user scope. So the cgroup's `memory.peak` is that clone alone. Systemd prints
  the same counter as the tick unit's "memory peak".
- "Anon" is anonymous memory. "File" is page cache. The probe reads both from the cgroup.

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

- Runs 1–4 were 2026-11-03 ~20:51. Runs 5–8 were ~21:06–21:10 (local).
- "private" means a store that the probe seeded outside the scope, from the checkout's HEAD tree. The probe falls back
  to it when the live store is unreadable. The checkout that the probe measures is the same.
- Records: `D:\ClaudeWork\rimmandrake\clone_mem_probe\run-*.json` (scratch; each holds a 0.5 s timeline).

## The answer

- **git holds it, not `scratch_clone.py`.** `scratch_clone.py` peaks at ~24 MB. The peak is `git read-tree -mu HEAD`,
  the checkout. It lasts from t≈2 s to the end of the clone (~13 s wall).
- **The peak is page cache, not process memory: 75–93 % of the peak is `file`.**
  - `read-tree` writes the ~3.8 GB worktree. The kernel charges the written pages to the cgroup that wrote them. Those
    pages are mostly dirty at the peak.
  - Anon is ~0.2 GB.
- `git read-tree` shows ~2.8 GB **VmRSS**, of which 0.21 GB is RssAnon. The rest is the store's packfiles mmapped,
  shared and reclaimable. Read by VmRSS alone, `git read-tree` looks like a 2.8 GB process. `git read-tree` is not a 2.8 GB process.
- **The host feels 0.1–1.1 GB, not 2–4.5 GB.** The lowest MemAvailable during a clone was 0.13–1.06 GB below its start.
  The reason is that clean page cache counts as available.
- **One clone alone reaches 4–4.5 GB of cgroup peak** (runs 5, 6).
  - Some of the written worktree is still charged at the high-water mark. How much varies run to run (0.98–4.5 GB over 8
    runs).
  - So two clones are not needed for a tick's 4–5 GB "memory peak". That peak is the
    high-water mark of the whole `rm-relentless.service` run. The page cache of ONE clone produces as much.
  - Workers are their own systemd units. So that number does not include the workers.
  - UNMEASURED: the larger peaks in the tick journal over 2026-10-31 to 2026-11-03, up to 10.9 GB. Nobody took them
    apart. The source of those peaks is `journalctl --user -u rm-relentless.service | grep "memory peak"`.

## What this means for the stop lines

- `min_mem_available_gb` (6) and the 3 GB host stop line read MemAvailable. MemAvailable already treats this page cache
  as available.
- A budget of 4–5 GB per clone against those lines overcounts the clone several times over. The measured figure is
  ~0.5 GB of MemAvailable per concurrent clone (worst seen 1.06 GB).
- Recheck with `clone_mem_probe.py --runs 1 --check`. Its exit codes:
  - 0 while >= 60 % of the peak is page cache and a git process is the largest anon holder;
  - 1 when either stops being true;
  - 2 when it could not measure: no user scope, the clone failed, or too few samples / too small a peak to have seen the
    checkout.
- The recheck needs neither the live store, GitHub nor Lodestar. It falls back to a private store and a TMPDIR record
  dir, and prints which it used.
