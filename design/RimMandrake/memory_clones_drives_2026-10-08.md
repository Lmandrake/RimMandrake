# Memory, clones, drives and configuration — audit and redesign (2026-10-08)

**Scope.** Archmagi (Windows 11 host, 63.4 GB) running the RimMandrake + RimFlow fleet in WSL2
Ubuntu. Every number below was measured on 2026-10-08 06:25–06:40 PDT unless marked otherwise;
the command that produced it is named so it can be re-run.
**Trigger.** 2026-10-07 23:08–23:20: 23 OOM kills in the FOUNDRY seat, including the Claude
process itself, after a subagent cloned the repo into `/tmp/claude-1000/pushclone` (tmpfs) while
the same seat ran the 16-worker selftest suite.
**Status.** Design only. Nothing in this pass changed configuration. Plans are options for the
owner; the recommendation is §7.

---

## 1. Headline findings

1. **The 10-07 incident is the sixth tmpfs-charge OOM in eight days, not the first.** The kernel
   OOM reports (`journalctl -k -b N`, "Memory cgroup stats" blocks) show seat memcgs dying with
   tmpfs pages (`shmem`) of 6.4 GB (10-01), 3.1–3.6 GB (10-04), 9.0 GB (10-05 21:19),
   8.8 GB (10-06 22:42), 9.65 GB (10-07 15:17) and 7.4 GB (10-07 23:08). **The Claude process
   itself was killed in five of them** (10-01 07:55, 10-05 21:19, 10-06 22:42, 10-07 15:17,
   10-07 23:16). Lessons were filed after 10-06 and 10-07; the behaviour recurred within hours both
   times. Prose lessons do not stop it.
2. **There is a second, equally large failure class: parallel test fan-out.** Boot -2
   (09-27 → 10-06) logged 96 OOM kills, 91 of them `python3`. From 10-04 00:27 to 10-05 13:43 the
   seat memcgs died at **anon ≈ 10.1 GB with shmem < 200 MB** — pure process memory, no tmpfs.
   Individual killed harness processes were 1.2–5.1 GB anon. `run_selftests.py` defaults to
   `DEFAULT_WORKERS = 16` (line 74, "IO-bound, not CPU-bound") inside a 10 GB seat that also hosts
   Claude. The 10-08 suite run lost 4 of 336 tests to rc 137
   (`Transient/selftest_after_l0_20261008.txt`). 16 × 1.5 GB ≈ 24 GB of demand against a 10 GB cap.
3. **tmpfs charges outlive their writer.** After 23:20 the FOUNDRY scope held ~9.2 GB of shmem
   with only a `sleep` loop alive. Resident tmpfs pages keep their memcg charge after the writer
   exits, and every ancestor (`claude-seats.slice`) keeps counting them; on kernel 6.18 a removed
   scope can linger as an offline memcg still holding them (corrected after GPT review, §8 #5).
   Restarting the seat therefore does not free the memory — deleting the files (with no open
   handles) or swapping them out does.
4. **Both seats have hit their 10 GB cap this boot.** `memory.peak`: FOUNDRY 10 242 MB
   (`oom_kill 23`), BENCH 10 240 MB (`max` events 250 884, no kill — page cache absorbed it).
   The slice peaked at 21.2 GB of its 24 GB.
5. **RimWorld can need 20 GB.** `Transient/memory_audit_synthesis_2026-09-08.md`: peak RSS
   20.17 GB with 599 mods; steady state 7.3–18.8 GB. Right now it is running at 3.2 GB working
   set / 6.2 GB private (`Get-Process`). The `.wslconfig` comment budgeted "~9 GB"; that is out of date.
6. **The host budget only closes with ~1–2 GB to spare** at simultaneous peaks:
   WSL cap 36 GB + RimWorld 20.2 GB + Windows/apps ≈ 6 GB (estimate; commit never measured)
   ≈ 62 GB of 63.4 GB. `vmmemWSL` holds 18.5 GB working set while the guest reports 2 GB used + 6 GB
   cache — `autoMemoryReclaim=gradual` returns memory slowly.
7. **~240 GB of the 337 GB on the ext4 disk is reclaimable debris** (§2.4). The worst single item:
   `mirror.git` carries **71.35 GiB of `tmp_pack_*` garbage from 42 aborted fetches**
   (10-03 23:25 – 10-04 00:26 and 10-06 12:20 – 22:55, one every 5–6 min — the `rm-mirror.timer`
   cadence) against a 5.82 GiB real pack.
8. **Six clones borrow objects from the live seat clones via `alternates`** (`_fwY_*` ×5 →
   foundry; `reconcile`, `~/.cache/pyrelands_replay_*` → bench). A `git gc --prune` in a seat can
   silently corrupt all of them.
9. **The guard rails themselves contain the anti-pattern.** `.claude/hooks/block_shared_tree_merge.py`
   lines 24–25 recommend `git worktree add --detach /tmp/claude-1000/merge-<x> origin/main` — a
   full checkout on tmpfs. And the push the 10-07 subagent cloned for is already served by
   `Utils/publish.py`, which builds commits in a private index with no checkout.

---

## 2. Audit

### 2.1 Physical memory, swap, WSL configuration

| Item | Value | Source |
|---|---|---|
| Host RAM | 63.4 GB; 20.7 GB free at 06:30 | `Win32_OperatingSystem` |
| WSL VM | 35 GiB visible (`memory=36GB`), 14 vCPU | `free -g`, `nproc` |
| Swap | 16 GB partition `/dev/sdc`, 1.4 GB used; `swappiness=60` | `swapon --show` |
| `.wslconfig` | `memory=36GB swap=16GB`, `[experimental] autoMemoryReclaim=gradual sparseVhd=true` | `C:\Users\Mandrake\.wslconfig` |
| `/etc/wsl.conf` | `systemd=true` | |
| `vmmemWSL` (Windows view) | 18.5 GB working set, 19.2 GB private | `Get-Process` |
| RimWorldWin64 now | 3.2 GB WS, 6.2 GB private | `Get-Process` |
| RimWorld peak | 20.17 GB (599 mods); steady 7.3–18.8 GB | `Transient/memory_audit_synthesis_2026-09-08.md`, `rimworld_memory_audit_2026-09-12.md` |
| Other Windows top procs | Memory Compression 0.76, Defender 0.56, dotnet 0.51, Spotify ×2 0.76, Steam ×2 0.72, Dropbox 0.39, Chrome… ≈ 4 GB | `Get-Process` |

Note the slice file still sets `MemorySwapMax=8G` and its comment assumes an 8 GB swap; swap is now 16 GB.

### 2.2 Cgroups: who uses what

`/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/…` (`memory.current/peak/events/stat`):

| Unit | current | peak (this boot) | max | notes |
|---|---|---|---|---|
| `claude.slice/claude-seats.slice` | 9.36 GB | 21.18 GB | 24G (+8G swap) | |
| `claude-seat-BENCH-768` | 5.35 GB (anon 0.83, file 4.33) | 10.24 GB | 10G / 2G swap | 250 884 `max` events, 0 kills |
| `claude-seat-FOUNDRY-683` | 0.18 GB | 10.24 GB | 10G | **23 oom_kill**, 6 749 `oom` |
| `claude-seat-unknown-636` (EMERGENCY) | 4.16 GB (file 3.47) | 4.26 GB | 10G | `AGENT_SEAT` unset |
| `claude-seat-unknown-539` (RC Server) | 53 MB | 281 MB | **16G** | over-provisioned |
| `app.slice` | 165 MB | 3.50 GB | none | unbounded |
| `rm-artpiped.service` | 114 MB | 164 MB | none | |
| `rm-codebase-health.service` | — | 54 MB | none | every 15 min |
| `rm-mirror.service` | — | 13 MB | none | every 5 min; runs code **from the foundry working tree** |
| `lodestar-sync.timer` (system) | — | not recorded | none | hourly |

Most of a healthy seat's `memory.current` is page cache (`file`). Clean cache is reclaimable;
dirty cache must be written back first and can throttle writers (§8 #4). `file` *includes*
`shmem`, so `file` alone does not prove harmless cache — check `shmem` separately.

### 2.3 OOM history (all retained boots, `journalctl -k -b -14 … 0`)

| Boot (dates) | Kills | Constraint | What died | Driver |
|---|---|---|---|---|
| -14 (08-14) | 1 | **global_oom** | Claude seat at 27.4 GB anon | pre-bounding; fixed by `claude_bounded.sh` |
| -13, -12 (08-14→08-28) | 3 | memcg | python3, 2 Claude seats | |
| -10 (09-03→09-05) | 10 | memcg | python | test fan-out; led to `OOMPolicy=continue` |
| -8 (09-09→09-14) | 3 | memcg | python | |
| -6 (09-17→09-19) | 11 | memcg | chrome-headless, python | anon 10.0 GB |
| **-2 (09-27→10-06)** | **96** | memcg | 91 python3, 3 git, 2 claude | shmem 6.4 GB (10-01); **anon ≈ 10.1 GB, shmem < 0.2 GB (10-04/05 fan-out)**; shmem 3.1–3.6 GB (10-04); shmem 9.0 GB (10-05 21:19, Claude killed) |
| -1 (10-06→10-07) | 7 | memcg | python3, git, **claude ×2** | shmem 4.3→8.8 GB (10-06 22:42); 9.65 GB (10-07 15:17) |
| 0 (10-07→) | 23 | memcg | 16 python3, 6 git, **claude** | shmem 7.4 GB + 16-worker suite |

Since 08-14 there has been **no global OOM** — the bounding works as designed. What remains is
that a seat's own tools kill its own Claude process.

The lesson `20261008T022031Z-BENCH-git-fetch-from-10g-capped-seat.md` attributes the 10-07 15:17
shmem to `git fetch`. That attribution is **unproven**: ordinary pack writes into an ext4 repo are file pages, not
shmem. The memcg held 9.65 GB of shmem at the kill; shmem also counts shared anonymous mappings,
so this proves RAM-backed pages, not necessarily visible `/tmp` files. Who wrote them is unknown.

### 2.4 Clones, worktrees, caches (`du -sh`, `.git` inspection)

All on the ext4 VHD (`/dev/sdd`, 1007 GB, 337 GB used;
`C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx` = 339.9 GB
on C:, which has 2.6 TB free).

| Path | Size | Kind | Last touched | Verdict |
|---|---|---|---|---|
| `/home/mandrake/rm/bench` | 16 GB (`.git/objects` 8.9 GB) | full clone | live | seat |
| `/home/mandrake/rm/foundry` | 17 GB (8.7 GB) | full clone | live | seat |
| `/home/mandrake/rm/mirror.git` | 78 GB | bare | live (timer) | **71.35 GiB garbage**: 42 `tmp_pack_*` |
| `/home/mandrake/rm/_fwY_{base,blood,gate,quarry,tanker}` | 6.2 GB each (pack 318 MB) | clone, **alternates → foundry** | 10-05 | stale, fragile |
| `/home/mandrake/rm/reconcile` | 6.1 GB | clone, alternates → bench | 10-05 | stale |
| `/home/mandrake/rm/drain` | 3.5 GB | no `.git` | 10-02 | stale |
| `/home/mandrake/rm/fwx,fwx2..5` | 24 MB–1.2 GB | partial trees, no `.git` | 10-05 | northstar run roots, stale |
| `/home/mandrake/wt/impl-*` (11) | 9.1–9.4 GB each, 81 GB total for `wt/` (hard-linked packs) | full local clones | 10-02 | stale; worktrees/side clones retired 10-02 |
| `/home/mandrake/wt/gitlab` | 30 GB | not a repo | 10-01 | unknown purpose; owner to judge |
| `~/.cache/{bench,pyrelands_replay_1607507,stillsand_s2_replay,warscar_push}` | 5.9 GB each | repo copies (pyrelands: alternates → bench) | 10-05 | ad hoc agent clones; stale |
| `~/.cache/uv`, `~/.cache/pip` | 13 GB, 2.8 GB | package caches | | keep or `uv cache prune` |
| `D:\Luke\dev\RimMandrake` | — | read-only mirror on drvfs | | kept by `rm-mirror.timer` |

### 2.5 tmpfs / RAM-backed storage

| Mount | Size | Used now | Notes |
|---|---|---|---|
| `/tmp` | 18 GB (`size=50%`, `nr_inodes=1m`) | 543 MB; **7 043 entries** | leaked test dirs: `ns_mock_*` ≈ 1 200, `gs_*` 479, `bacta_st_*` 188, `nsjudge_st*` 135 |
| `/tmp/claude-1000` | — | 408 MB | Claude Code scratchpads + background-task `.output` files; one session reached **6.2 GB** on 10-05 (`/home/mandrake/rm/tmpusage.txt`) |
| `/dev/shm` | 18 GB | 0 | |
| `/run/user/1000` | 3.6 GB | 28 KB | |

`/tmp` and `/dev/shm` together can absorb 36 GB — more than the VM. Their pages are charged to
whichever cgroup first touched them; writers outside the seat slice (timers, `app.slice`) have no
ceiling at all.

Big writers into `/tmp` found in code (no clone/worktree creation exists in code — every clone
above was made by hand or by an agent): `Utils/art/gametex.py:48` (`/tmp/rm_gametex`, 26 MB);
`gen_*_register.py` texture caches in `/tmp/claude-1000`; `droid_canon_fill.py:14`;
un-cleaned `mkdtemp` in `biomes_compose.py:236`, `FlowWorks/northstar/prep_site.py:330`,
`northstar_driver/judge_cli.py:114`; `run_selftests.py:73` timing cache. Claude Code 2.1.286
honours `CLAUDE_CODE_TMPDIR` (string present in the binary; its scope — scratchpad vs. socket
dir only — must be confirmed before relying on it). It also ships **`CLAUDE_CODE_TOOL_MEMORY_LIMIT`**
(5 occurrences in the 2.1.286 binary, alongside "tool cgroup" and `CLAUDE_CODE_TOOL_MEMORY_CGROUP_EXCLUDE`):
a built-in child cgroup that caps Claude's tool commands collectively. It is unset on every seat.
This audit missed it until the GPT review (§8 #15).

### 2.6 RimFlow and the git workflow

RimFlow is not a separate repo; it is `src/RimMandrake/rimflow/`, an append-only JSONL ledger
(`infrastructure/state/ledger/`). It does no cloning, pushing or game launching. Seats are ledger
identities (BENCH, FOUNDRY, OWNER) mapped to window clones `/home/mandrake/rm/<seat>` launched via
`claude_bounded.sh`. Pushing is `./publish` (`Utils/publish.py`: private-index commit, `pull
--rebase`, push, 8 retries). The game is serialized by `rimflow bridge take/release`.
Worktrees were switched off by the owner on 2026-10-02 (`.claude/hooks/block_worktrees.py`).

### 2.7 `claude_bounded.sh` history

`1378ecbb2` (08-14) diagnosis → `6a291e9a4` bounded at 6G → `b507e151e` raised to 10G (idle tree
measured 2.81 GB = 47 % of 6G) → `c68f7d330` slice 24G ("five seats × 10G = 50 GB against a 36 GB
VM") → `ea2840e51` (09-05) `OOMPolicy=continue` → `f610d7eac`, `1db4ed8d3` (10-02) housekeeping.
The wrapper ends in `exec systemd-run --scope … claude`, so nothing runs after Claude exits — which
is why a killed Claude leaves the terminal in SGR mouse-tracking mode.

### 2.8 Failure classes

| ID | Class | Evidence | Currently prevented? |
|---|---|---|---|
| F1 | Large tmpfs writes (clones, scratch, task output) charged to a seat | 6 incidents 10-01→10-07 | No (lessons only) |
| F2 | Parallel test fan-out exceeds seat cap | ~70 kills 10-04/05; 4 tests 10-08 | No |
| F3 | Charge persists after writer dies / seat restarts | 9.2 GB overnight 10-07 | No |
| F4 | One seat exhausts the VM (global OOM) | 08-14 | **Yes** (scope + slice) |
| F5 | Disk bloat from stale clones and aborted fetches | ~240 GB | No |
| F6 | Alternates into live seat clones | 7 clones | No |
| F7 | Terminal left in mouse mode after a kill | 10-07 | No |
| F8 | Unbounded non-seat writers (timers, `app.slice`) | `app.slice` peak 3.5 GB | No |
| F9 | Host overcommit: WSL 36 + RimWorld 20 + Windows | 1–2 GB margin | Marginal |
| F10 | Victim selection: the kernel kills Claude rather than the balloon | 5 Claude kills | No |

F10 needs comment: when the balloon is tmpfs, no process "owns" it, so the OOM killer picks the
largest killable process — often Claude or a harness — and killing it frees nothing.

---

## 3. Plan A — Guard rails in place (minimal structural change)

**Idea.** Keep the layout; make the dangerous things impossible or loud at the points where they happen.

Changes:
1. **Per-seat TMPDIR on ext4.** `claude_bounded.sh` exports `TMPDIR` and `CLAUDE_CODE_TMPDIR` =
   `/home/mandrake/.seat-tmp/<SEAT>` (0700). A `systemd-tmpfiles` user rule ages entries out after
   3 days (ext4 is not cleared at boot, unlike tmpfs). Page cache on ext4 is reclaimable, so a 12 GB
   clone becomes disk I/O, not an OOM.
2. **Shrink tmpfs.** `tmp.mount` drop-in `size=4G`; `/dev/shm` `size=2G` (fstab). A stray clone into
   `/tmp` now fails with ENOSPC after 4 GB instead of killing a seat.
3. **Hook.** Extend `block_worktrees.py` (PreToolUse/Bash) to refuse `git clone`/`worktree add`/
   `cp -r` of a repo whose target is under `/tmp` or `/dev/shm`, and point at `./publish`. Fix the
   `/tmp` recommendation in `block_shared_tree_merge.py:24-25`.
4. **Test fan-out bound.** `run_selftests.py`: default workers =
   `clamp(1, 16, (memory.max − memory.current − 2 GB reserve) / 1.5 GB)` read from the caller's
   cgroup; each test runs under `systemd-run --user --scope -p MemoryMax=4G -p MemorySwapMax=0`
   so a balloon dies alone with a clear `KILLED` and Claude is never the victim.
5. **Seat soft limit.** `-p MemoryHigh=8G` on each seat: the kernel throttles and reclaims before
   the hard 10G kill, buying time and producing a `high` event to alert on.
6. **Watchdog.** A 1-minute user timer reads `memory.events` and `memory.stat` of every seat; if
   `oom_kill` increases or `shmem > 2 GB` it writes a RimFlow ledger event and a Windows toast
   naming the seat and the largest `/tmp` paths.
7. **Terminal reset.** Drop `exec`; after `systemd-run` returns, emit
   `ESC[?1000l ESC[?1002l ESC[?1003l ESC[?1006l ESC[?1015l ESC[?2004l ESC[?1049l ESC[?25h` and
   `stty sane`, then exit with Claude's status.
8. **Housekeeping, once.** Delete the 42 mirror `tmp_pack_*` files (71 GB), lower the RC Server's
   cap from 16G to 2G, set `AGENT_SEAT` for EMERGENCY/Server.

Memory budget (WSL 35 GB):

| Consumer | Bound | Expected |
|---|---|---|
| 4 seats (claude-seats.slice) | 24G total, 10G each, High 8G | 1–3 GB each idle |
| …of which harness workers | per-test 4G, count from headroom | ≤ ~5 GB per seat |
| RC Server | 2G | 0.3 GB |
| tmpfs `/tmp` + `/dev/shm` | 4G + 2G | < 1 GB |
| Timers, artpiped, app.slice | unbounded | 0.2–3.5 GB |
| Kernel + page cache headroom | remainder | ~5 GB |
| **Host:** WSL 36 + RimWorld 20.2 peak + Windows ~6 | | **≈ 62 / 63.4 GB** |

Eliminates: F1 (both by relocation and by ENOSPC), F2 killing Claude, F7, most of F10.
Detects only: F3 (smaller now), F8. Does not address: F5 beyond one cleanup, F6, F9.
Cost: ~1 day. Risk: low. Each item is independently revertible.
New trouble: tests that silently relied on tmpfs speed get slower on ext4 (`rimflow/model.py:38,61`
records the opposite — a test that only passed on tmpfs — so this also flushes real bugs); per-test
scopes add ~30 ms × 336 tests; a 4 GB `/tmp` will expose any legitimate large `/tmp` user as ENOSPC
(e.g. `gametex` 26 MB — fine); `/tmp` shrink needs a remount that fails if usage exceeds the new size.

Migration: (1) wrapper changes land in the repo; each seat picks them up on next launch — no fleet
restart needed. (2) `run_selftests.py` change is a normal commit. (3) tmpfs resize is
`systemctl daemon-reload && mount -o remount,size=4G /tmp` after checking usage < 4G; no reboot.

---

## 4. Plan B — Relocate and re-budget (structural)

**Idea.** Everything in A, plus: move all bulk scratch and all clones to one managed place on ext4
with one shared object store; separate harnesses from Claude into their own cgroup budget; bound
every non-seat writer.

Changes beyond A:
1. **One object store, owned by nobody's working tree.** Re-purpose `mirror.git` (after deleting its
   garbage and `git gc`) as `/home/mandrake/rm/store.git`, fetched only by the mirror timer. Seat
   clones and every scratch clone use `--reference store.git`; rewrite the 7 existing alternates
   (`_fwY_*`, `reconcile`, `pyrelands`) to point at the store or delete them. The store is never
   pruned by agents (`gc.pruneExpire=never`, `gc.auto=0`), so no seat `gc` can corrupt a borrower.
2. **One sanctioned scratch-clone tool.** `Utils/scratch_clone.py <name>` →
   `/home/mandrake/rm/scratch/<SEAT>/<name>`, `--reference store.git`, `--no-checkout` by default,
   sparse checkout on request, recorded in a registry with owner/seat/expiry; a daily timer deletes
   expired ones. A full working tree costs ~6 GB of disk and ~0 GB of RAM. The hook from A points here.
   (This is not a worktree and does not re-open what the owner retired on 10-02: no shared index,
   no side branches; it pushes through `./publish` like any clone.)
3. **Harness slice.** A sibling `rm-harness.slice` (MemoryMax 12G, MemorySwapMax 2G).
   `run_selftests.py` and the northstar/judge drivers launch their workers there
   (`systemd-run --user --scope --slice=rm-harness.slice`). Tests then compete with tests, never with
   a Claude process. Workers are admitted by a memory-token pool (flock'd counter in
   `/run/user/1000/rm-harness/`) sized from per-test `memory.peak` recorded in
   `selftest_timings.json`.
4. **Services slice.** `rm-services.slice` (MemoryMax 3G) for `rm-mirror`, `rm-codebase-health`,
   `rm-artpiped`, Lodestar sync; run `mirror.py` from a pinned copy, not from the foundry working tree.
5. **Re-budget seats.** Claude itself is small (killed Claude processes were 0.3–0.64 GB anon; idle
   tree 2.81 GB). With harnesses moved out: per seat MemoryMax 7G / MemoryHigh 5G; slice 16G.
6. **Disk.** Delete `wt/impl-*` (≈ 81 GB), `mirror.git` garbage (71 GB), `_fwY_*` (31 GB),
   `~/.cache/*` repo copies (23.6 GB), `reconcile`, `drain`, `fwx*` (≈ 12 GB) — after the owner
   rules on `wt/gitlab` (30 GB). Then `fstrim -v /` so `sparseVhd` gives the space back to C:.
7. **Host side.** `autoMemoryReclaim=dropcache` instead of `gradual` (returns page cache promptly
   when RimWorld needs it) and update the `.wslconfig` comment to RimWorld's measured 20 GB peak.

Memory budget (WSL 35 GB):

| Consumer | Bound | Expected |
|---|---|---|
| claude-seats.slice | 16G (7G each, High 5G) | 1–3 GB each |
| rm-harness.slice | 12G (+2G swap), token-admitted | 0–12 GB |
| rm-services.slice | 3G | 0.3 GB |
| RC Server | 2G | 0.3 GB |
| tmpfs `/tmp` + `/dev/shm` | 4G + 2G (charged inside the above) | < 1 GB |
| Kernel + page cache headroom | 35 − 33 = ~2 GB guaranteed; more in practice | |
| **Host** | 36 + 20.2 + ~6 | **≈ 62 / 63.4 GB** |

Eliminates: F1, F2, F3 (tmpfs is no longer where big data goes), F5, F6, F7, F8, F10.
Detects: F9 (via the watchdog and Windows commit counter added to it).
Cost: ~3–4 days including measurement of per-test peaks. Risk: medium.
New trouble: a shared harness slice means one seat's 336-test sweep can starve another seat's
quick check (mitigation: token pool with per-seat fair share); a 7G seat cap is tighter for any
heavy in-process work an agent runs outside the harness (MEM_MAX override still exists); the
store becomes a single point of failure for every `--reference` clone (mitigation: it is
rebuildable from GitHub in ~10 min, and `git repack -a` in a clone dissociates it); disk deletions
are irreversible — needs an owner pass over the list first.

Migration: phase 1 = Plan A. Phase 2 = store + scratch tool + rewrite alternates, while seats keep
running. Phase 3 = harness/services slices (wrapper and `run_selftests.py` changes; seats relaunch
naturally). Phase 4 = re-budget seats down to 7G only after a week of `memory.peak` data shows Claude
trees stay under 4 GB.

---

## 5. Plan C — Central broker for git and tests (service-oriented)

**Idea.** Agents stop doing heavy work themselves. A user daemon (modelled on `rm-artpiped`) owns
every expensive operation and runs it inside its own fixed budget.

Changes:
1. `rm-brokerd.service` in `rm-broker.slice` (MemoryMax 14G) with a queue in
   `/home/mandrake/rm/broker/`. Verbs: `fetch` (serialised; one network fetch per interval into the
   store, seats then fetch locally from the store), `scratch <name>` (as Plan B's tool, but executed by
   the broker), `test <suite>` (runs `run_selftests.py` with a global worker pool sized from
   measured peaks), `publish` (wraps `./publish` with a global push lock).
2. Seats get a hard cap of 6G: they no longer run anything heavier than Claude and small scripts.
3. A hook denies `git clone`, `git fetch` of origin and `run_selftests.py` from inside seats and
   tells the agent to use `rmbroker <verb>`.
4. Plan A's tmpfs shrink, terminal reset and watchdog are included.

Memory budget (WSL 35 GB):

| Consumer | Bound | Expected |
|---|---|---|
| claude-seats.slice | 14G (6G each) | 1–3 GB each |
| rm-broker.slice (git + tests) | 14G | 0–14 GB, globally scheduled |
| rm-services.slice | 3G | 0.3 GB |
| tmpfs | 4G + 2G | < 1 GB |
| Headroom | ~4 GB | |
| **Host** | 36 + 20.2 + ~6 | **≈ 62 / 63.4 GB** |

Eliminates: everything Plan B does, plus concurrent-fetch storms and test runs from two seats
colliding, with one global admission policy.
Cost: 1–2 weeks; a new daemon with its own state, retries, logs and failure modes.
Risk: high. The broker becomes a single point of failure for pushing and testing; when it is down,
every seat stalls. Agents must learn a new verb set, and agents routinely route around tooling they
find in the way (the 10-07 subagent cloned rather than use `./publish`). Asynchronous test results
complicate the agent loop (poll vs. block). Debugging moves from "what did my shell do" to "what did
the daemon do".

---

## 6. Plan D — Capacity only (named so it can be rejected on the record)

Raise `.wslconfig` to 44 GB and seats to 14 GB. Rejected: 44 + RimWorld 20.2 + Windows ~6 = 70 GB on
a 63.4 GB host; the host itself would page under a heavy RimWorld session. It also does nothing for
F1/F3 — a 12 GB clone into tmpfs kills a 14 GB seat just as well when Claude and a test suite share it.

---

## 7. Comparison and recommendation

| | A guard rails | B relocate + re-budget | C broker | D capacity |
|---|---|---|---|---|
| F1 tmpfs clone | eliminated | eliminated | eliminated | no |
| F2 test fan-out kills Claude | eliminated (per-test scope) | eliminated (separate slice) | eliminated | no |
| F3 sticky charge | reduced | eliminated | eliminated | no |
| F5 disk bloat | one-off | managed | managed | no |
| F6 alternates | no | eliminated | eliminated | no |
| F8 unbounded services | detected | bounded | bounded | no |
| F9 host overcommit | unchanged | slightly better (dropcache) | same as B | **worse** |
| Effort | ~1 day | ~3–4 days, phased | 1–2 weeks | 1 hour |
| Risk | low | medium | high | high |

The "eliminated" cells above were written before the GPT review and are too strong (§8 #2, #13):
read them as "removes the documented path", not as guarantees. In particular, any plan whose seat
caps sum above the slice cap (B: 4 × 7G under 16G; C: 4 × 6G under 14G) can still produce an
ancestor-level OOM that picks a Claude process from any seat.

**Recommendation (revised after GPT review): "B-lite", in this order.**

| Phase | Change | Why first |
|---|---|---|
| 0 — today | `run_selftests.py` `DEFAULT_WORKERS` 16 → **1** inside a seat; `--workers N` only when launched into the harness slice | Cheapest change against the largest documented kill class (GPT #9; owner's 10-08 note on 16-worker fan-out) |
| 0 — today | Set `CLAUDE_CODE_TOOL_MEMORY_LIMIT` (start at 6G under the 10G seat) in `claude_bounded.sh`; confirm in the debug log that the tool cgroup was created and not silently skipped | Tool commands — including a tool writing to tmpfs, whose shmem is charged to the tool cgroup — then die before Claude does. Built in, no new machinery (GPT #15) |
| 0 — today | Terminal reset after Claude exits (drop `exec`) | Trivial, independent |
| 0 — today | Hook refusing `git clone`/`worktree add`/repo `cp -r` into `/tmp` or `/dev/shm`; fix `block_shared_tree_merge.py:24-25` | Removes the exact path of the six incidents; a guard rail, not containment |
| 1 | Validate `CLAUDE_CODE_TMPDIR` + `TMPDIR` → `/home/mandrake/.seat-tmp/<SEAT>/` on 2.1.286 (foreground/background output, scratchpad, sockets, sandboxed Bash, resume) before switching seats | GPT #8: Claude itself lives in `/tmp/claude-1000` |
| 1 | Harness slice `rm-harness.slice` 12G; workers launched with explicit `--slice=` and fail closed if `/proc/<pid>/cgroup` shows otherwise; admission by live systemd units (not a counter) | GPT #1, #10 |
| 1 | Watchdog on `memory.events`/`memory.stat`/PSI, plus `file_dirty`/`file_writeback` | Detection for what remains |
| 2 | Disk: quarantine (move, not delete) stale clones after checking dirty/untracked files, local refs and remote reachability; owner rules on `wt/gitlab`; delete the 42 `tmp_pack_*` after the mirror timer is paused and the cause of aborted fetches is found | GPT #11, #13 |
| 2 | Store: copy objects the borrowers need into `store.git`, `git fsck` every borrower, then rewire; durable clones use `--reference … --dissociate` | GPT #12 |
| 3 | Only after the above is stable: shrink `/tmp` (8G, not 4G — a single session's task output reached 6.2 GB), bound services in their real managers (`lodestar-sync` is a *system* unit), measure Windows commit while RimWorld is loaded before touching `.wslconfig` | GPT #3, #8, #13 |
| deferred | Tighter seat caps (7G), the broker (Plan C) | No evidence yet that they are needed; both add risk |

Seats keep 10G / 24G slice until a week of `memory.peak` data, with tools capped and harnesses out of
the seat, says otherwise.

---

## 8. GPT adversarial review

**Reached: yes.** `src/RimMandrake/Utils/gpt_consult.py` → `codex.exe exec`, model `gpt-6.1-sol`,
high effort, 2026-10-08 ~06:45–07:05 PDT. Prompt: the full pre-review draft of this document plus a
four-part attack brief (root cause, plan failure modes, budgets, over-claims). Its verdict: *"The two
main causes are credible. The claimed eliminations are not. I would choose a smaller B/A hybrid, and
move harness isolation ahead of shared-store work."* Its cheapest single change: `DEFAULT_WORKERS`
16 → 1.

| # | Severity | GPT's point (condensed) | Accepted? | What changed |
|---|---|---|---|---|
| 1 | Critical | `systemd-run --user --scope` from inside a seat does **not** nest under the seat; 16 × 4G per-test scopes would escape the seat's limit | **Yes** | Plan A item 4 is wrong as written. Revised plan places workers in an explicit harness slice and fails closed after checking `/proc/<pid>/cgroup` |
| 2 | Critical | Seat caps summing above the slice cap (B 28G under 16G, C 24G under 14G) leave ancestor OOMs that can kill Claude | **Yes** | Seat caps stay 10G/24G; 7G deferred; "eliminated" claims qualified |
| 3 | Critical | Host budget mixes WS, private bytes, commit and an estimate; `dropcache` is idle-triggered, not on-demand | **Yes** | Host margin labelled as an estimate; phase 3 measures Windows commit/available RAM while gaming before any `.wslconfig` change |
| 4 | High | Ext4 page cache is not "harmless": dirty pages throttle; git needs anon memory | **Yes** | §2.2 reworded; watchdog adds `file_dirty`/`file_writeback`/PSI |
| 5 | High | tmpfs charges are not simply "reparented on removal"; on 6.18 offline memcgs can retain them; ancestors already count them | **Yes** | §1 #3 rewritten |
| 6 | High | shmem *can* swap under `MemorySwapMax=2G`; deleted-but-open files keep storage | **Yes** | Noted in §1 #3; incident capture should record `memory.swap.current` and deleted-open files |
| 7 | High | `shmem` ≠ visible `/tmp` files (includes shared anon mappings); `file` includes `shmem` | **Yes** | §2.2, §2.3 fetch-attribution paragraph tightened |
| 8 | High | Shrinking `/tmp` to 4G can break Claude itself (a 6.2 GB task-output dir exists); `CLAUDE_CODE_TMPDIR` scope unvalidated | **Yes** | Shrink moved to phase 3, 8G not 4G, only after TMPDIR validation |
| 9 | High | The worker formula is not admission control; 1.5 GB/test unsupported; 4G cap rejects the 5.1 GB tests | **Yes** | Phase 0 is workers = 1 in seats; admission moves to the harness slice |
| 10 | High | A flock'd token counter leaks on SIGKILL, oversubscribes, can deadlock | **Yes** | Admission keyed on live systemd units, not a counter |
| 11 | High | Age-based cleanup deletes live work | **Yes** | Cleanup = quarantine after dirty/ref/reachability checks; tmpfiles directory locks for live sessions |
| 12 | High | `--reference` moves the hazard; the store may lack objects only foundry/bench hold | **Yes** | Copy + `fsck` before rewiring; `--dissociate` for durable clones |
| 13 | High | B doesn't bound all writers; system units can't join a user slice; broker has its own deadlocks; hooks are bypassable | **Yes** | Services bounded in their real managers; hooks called guard rails, not containment; broker stays deferred |
| 14 | Medium | Victim RSS and clipped `memory.peak` understate demand; rc 137 ≠ proof of OOM; hard links inflate summed disk estimates | **Partly** | Accepted in principle. The rc 137s on 10-08 coincide with logged memcg OOM kills of python3 in that scope at 23:08, so the OOM reading holds there. Disk: `wt/` was measured as a directory (81 GB, hard links counted once), but the "~240 GB" total is a sum of separately measured trees and may overstate — re-measure after quarantine |
| 15 | Medium | Audit missed `CLAUDE_CODE_TOOL_MEMORY_LIMIT`, which may fall back to uncapped if cgroup setup fails | **Yes — verified** | Present in the 2.1.286 binary (5 hits, with "tool cgroup" and an exclude variable). Added to phase 0, with a check that it actually engaged |

Net effect: the recommended plan stayed in Plan B's family but became smaller and reordered — harness
isolation and the built-in tool cap moved ahead of the object store; tmpfs shrink and seat re-budgeting
were deferred; every "eliminates" claim was weakened to "removes the documented path".
