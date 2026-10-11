# 06: Telemetry / time-series design proposal (2026-10-11)

Auditor dimension: the owner wants *"many, many metrics about the game state, a debug test's state, the disk's
state, memory... telemetry. Implementing telemetry time series so we can more easily monitor, detect, react to,
debug, and resolve game issues and changes."*

**Headline.** Most of the raw collectors already exist. Six of them write JSONL time series today, and three of
them are good. What is missing is the layer above them: one place that **indexes** every stream, one query verb
agents can use, **standing operation** of the two Windows-side collectors, and **disk**. Two collectors that
were built for this are not running at all (§1.3). So the MVP is mostly *turn on, join and index* rather than
*build new sensors*. That makes it about a day of work, not a week.

---

## 1. Inventory: what already emits data (measured 2026-10-11 ~08:55 PDT)

### 1.1 Table

| # | source | what it records | format / location | cadence | retention | state now |
|---|---|---|---|---|---|---|
| A | **JawaBench TPS record** (`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTps*.cs`, 10 files; doc `design/RimMandrake/tps_record.md`) | in-game, with no bridge call needed: `sample` window (ratio, tps, fps, gapMaxMs, simMs, tickMs, **gc count, heapMB**, coarse attribution of tick/tick lists/world/maps/components), `context` (per map: biome, **pawns, things**, worldPawns, heap, workingSet), `stall`/`longevent` incidents, `silence`/`resumed` (watchdog), `session` (pid, build, mod digest), `game`/`menu`/`save`, `shutdown`; also **archives Player.log** to `tps/logs` | JSONL segments `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps_<utc>_<session>_<pid>_<seg>.jsonl` | 1 sample per ~5 s of play, context every 60 s | `tps_settings.json`: retentionDays 7, retentionMB 256, logRetentionMB 1024 | **LIVE.** MEASURED: 21 segments, 12,011,773 B, 12,665 lines (sample 11,093, context 983, stall 42, silence 33, session 19), spanning 2026-10-10T15:30Z to 2026-10-11T15:55Z; 20 archived logs, 224,579,428 B |
| B | **health_observer.py** (`src/RimMandrake/Utils/health_observer.py`, doc `design/RimMandrake/game_health_record.md`) | Windows-side and outside the game: game.identity, game.cpu, game.mainthread, **game.memory** (WS/peak/private/pagefile), **sys.memory** (commit headroom), **log.growth** (Player.log rate/truncation), **log.milestones** (startup landmarks, 10k Verse.Log cap); every probe reports its own costUs | JSONL `...\JawaBench\health\observer_<utc>_<pid>_<seg>.jsonl` + `collector_last.json` | 5 s | per segment, no pruning found | **NOT RUNNING.** Last sample 2026-10-10 15:40 (`collector_last.json` mtime). The scheduled task named in its own docstring does not exist: `schtasks.exe /Query /TN "RimMandrake\Health Observer"` returned "cannot find the file specified". 4 segments, largest 2,644,698 B |
| C | **memwatch.py** (`src/RimMandrake/Utils/memwatch.py`, `rm-memwatch.timer`) | per cgroup (seat slices, harness): memory.events (oom_kill…), current/peak/max/swap, anon/file/shmem/dirty, PSI; optional `host` block (committed, avail, RimWorld WS/private, vmmem WS) | `~/.local/state/rm-memwatch/samples.jsonl` (+`.1`), `events.jsonl`, `state.json` | 1 min | rotates at 20 MB, keeps one `.1` (about 3 days) | LIVE for cgroups. MEASURED: 4,177 samples, **only 15 carry `host`**, because the unit runs `--no-host` (`src/RimMandrake/Utils/systemd/rm-memwatch.service:15`, `57729af83`: powershell.exe stole the owner's focus). Host memory from WSL is therefore dark, and B was meant to cover it |
| D | **RimPulse** (`src/RimMandrake/Utils/pulse/pulse.py` daemon on 127.0.0.1:8765, `pulse_core.py`, `widget/lantern.pyw`) | **state transitions**, not quantities: row key/kind changes (`pulse.jsonl`); alarm open/close with age (`metrics.jsonl`); the current snapshot (`pulse_now.json`); the widget POSTs `/api/probe` `rimworld_running` from `tasklist` every 5 s | `~/.local/state/rm-dashboard/` | collector 5 s | unbounded append | LIVE. MEASURED: pulse.jsonl 2,111 lines, metrics.jsonl 525 lines. It is already the alert/attention surface. It plots no series |
| E | **rimflow ledger** (`infrastructure/state/ledger/events/<SEAT>.jsonl` + frozen `events.jsonl`) | work events. Keys are `seat,event,state,ts` (not `kind`). MEASURED over the shards: note 1,554, file 1,325, claim 821, start 768, close 679, implemented 542, verify 424, lease 392, **bridge 350, game 259**, … | git-tracked JSONL | per action | forever (git) | LIVE. Already the authority for **game up/down/loading** (`./game`) and **bridge take/release**, so bridge hold time and game-state durations can be derived with no new sensor |
| F | **artpipe** (`D:\Luke\dev\_artpipe`) | `throughput.jsonl` per job (channel, elapsed_s, attempts, quota meter); `registry.jsonl` lifecycle events (validated/pass…); `art_status.json` rollup (stateCounts, spend, projection); queue dirs | JSONL + dirs on D: | per job | forever | LIVE. MEASURED: throughput 8,103 lines / 7.66 MB; registry 27,528 lines / 4.52 MB; pending 0, done 11,811, failed 776 |
| G | **northstar / proof results** (`src/RimMandrake/*/northstar/*.json`) | per run: `rows[]` each with `id,status,class,detail,block`, `wall_s`, `mod_hash`, `log_revive`, `control_noise`, `env` | one JSON per run | per run | forever, **in git** | LIVE. MEASURED: 231 result-like JSONs (GSS 149, FlowWorks 78), 104.5 MB on disk. **218 of them are git-tracked, 98,148,901 B.** That breaks the derived-artifacts rule in `~/.claude/CLAUDE.md` ("commit their provenance … not their bulk"). Latest GSS run: 105 rows, 105 PASS, wall 629 s |
| H | **LogTap** (`src/RimMandrake/Utils/validation_core.py:152`) | per proof run: polls RimBridge's 1,000-entry journal after every tick step, counts **lost** entries; Log.Clear plus a sentinel for the 10k Verse.Log cap | in memory, then into the proof JSON | per tick step | via G | LIVE in proof_all/proof_hose/v2. Lesson `infrastructure/state/lessons/20261011T142704Z-BENCH-full-list-log-budgets-are-blind.md` |
| I | **bridge observatory events** (`src/RimMandrake/Utils/rimdrive/obs_events.py`, `modcheck/obs_summary.py`; design `design/RimMandrake/bridge_validation_observatory.md`) | per bridge call: call_start/end, run_end with emitted/dropped/written | `D:\Luke\dev\_obs\runs\<run>.jsonl` | per call | none, 111 MB | **PARTIAL.** 44 runs, newest 2026-10-10T14:23. Only `rimdrive/session.py` and `modcheck/live_queue/common.py` emit. **The current proof path (`validation_core.py`, imported by proof_all.py) does not**, so the runs that matter now leave no per-call record |
| J | **jawa/map_comp_timing** (`JawaBenchMapCompTiming.cs:64`) | on demand: per-MapComponent ms per tick plus the owning mod (this is the source of the hose fix's 0.152 → 0.024 ms/tick) | bridge reply only | ad hoc | **none: the number lives in prose** | A one-off by design (per-component timing was "ruled out of the always-on path", per the header comment) |
| K | **objstore sampler** (`scratch_clone.py sample`, `rm-objstore.timer`) | store size, borrowers, fsck, **disk_free_bytes** (WSL root only) | `~/.local/state/rm-objstore/samples.jsonl` | 1 h | unbounded | LIVE, 73 samples. It is the **only** disk series that exists, and it covers one volume |
| L | **selftests** (`run_selftests.py`) | `~/.local/state/rm-selftests/last_run.json` + `records/<hash>/` (19) | JSON | per run | overwritten (last only) | LIVE, no history |
| M | **codebase health** (`rm-codebase-health.timer`, FOUNDRY clone) | rebuilds a page, `Transient/codebase_health_hook.log` | log | 15 min | Transient | LIVE, not a series |
| N | **Player.log** | engine log, 1,529,426 B now | text | continuous | overwritten per launch. A preserves the previous one | live. Hits the 10k message cap on the full list (lesson above) |
| O | **deploy / build** (`deploy_custom_mods.py --apply`, `winbuild.py`) | nothing. No event is written (no `jsonl`/ledger write found in either file) | — | — | — | **GAP**, and the most important one for change detection |

### 1.2 Host measurements taken for this report

- WSL root `/`: 1007G size, 541G used, 415G avail (df). C: 3.7T 44%, D: 3.7T 51%.
- **WSL VHDX** `C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-b999-497e-bf84-00c27e4b0562}\ext4.vhdx`: **975,065,579,520 B** (≈975 GB) on C:, holding a filesystem with 541G used. About 430 GB is allocated-but-free space that only a compaction reclaims. Nothing tracks that gap today, and it is exactly the "disk fills before we notice" class the owner named.

### 1.3 What is missing (§2 Gaps, merged here)

1. **Two collectors are built and not standing.** B has no scheduled task, and C runs host-less on purpose. As a result there is no host-memory series since 2026-10-10 15:40.
2. **Disk has no series at all** apart from K (WSL root, hourly). Nothing covers C:, D:, the VHDX size, the `_artpipe`/`_obs`/`_rmbuild` folders, the JawaBench `tps/logs` archive (224 MB), or the Saves folder.
3. **No deploy/build events,** so a per-tick regression cannot be tied to the change that caused it.
4. **No index or query layer.** Each stream has its own reader (`tps_record.py` 1,194 lines, `health_observer.py --read`, `memwatch.py host`, `pulse.py metrics`, `art_status.json`), and no single verb answers "show me X since 1h".
5. **Proof results are files in git** and are not a series. "Did check P7 flip from PASS to FAIL across runs" needs a hand-rolled glob.
6. **Per-MapComponent cost is never recorded,** only quoted in prose.
7. **Exceptions by source/mod** are not counted anywhere as a series. LogTap counts per run, inside G only.

---

## 2. Gaps

Merged into §1.3 above.

---

## 3. Metric catalogue

The `src` column names an existing source letter from §1. **NEW** marks a sensor that must be written. Series
names are dotted, and labels go in braces.

### 3.1 Game process
| series | src | cadence |
|---|---|---|
| `game.state` {up, loading, down} | E (`./game` events) + D probe + A session/menu/game | event |
| `game.load_s` (launch → `bridge.token` milestone) | B log.milestones, A session | per launch |
| `game.tps`, `game.tps_ratio`, `game.fps`, `game.gap_max_ms`, `game.stall_s` | A sample | 5 s |
| `game.tick_ms` and `game.attr_ms{stage}` (tick lists, world, maps, components) | A sample.attr | 5 s |
| `game.mapcomp_ms_per_tick{type,mod}` | J, **NEW** persisted: every `jawa/map_comp_timing` reply appended as points | on demand + scheduled (§5) |
| `game.heap_mb`, `game.gc_count` | A sample | 5 s |
| `game.ws_mb`, `game.private_mb`, `game.cpu_cores`, `game.mainthread_cores` | B | 5 s |
| `game.pawns{map}`, `game.things{map}`, `game.world_pawns` | A context | 60 s |
| `game.log_lines`, `game.log_bytes_per_s`, `game.log_capped` (10k Verse.Log cap reached) | B log.growth/milestones | 5 s |
| `game.errors{source_mod}`, `game.exceptions{type}` | **NEW** Player.log parser over A's archive + live log, attributed by stack frame namespace → mod | per log segment |
| `bridge.journal_lost` | H (per run), **NEW** as a series | per run |

### 3.2 Test runs
| series | src |
|---|---|
| `proof.check{mod,check}` = PASS/FAIL/UNMEASURED (as 1/0/null) | G rows[].status |
| `proof.run_wall_s{mod,script}`, `proof.rows{status}` | G |
| `proof.log_lost{mod}`, `proof.control_noise{mod}` | G/H |
| `selftest.result{file}`, `selftest.duration_s` | L (needs history kept: **NEW**, append per run) |
| `bridge.call_ms{tool}`, `bridge.calls_per_min`, `bridge.dropped` | I (once validation_core emits) |

### 3.3 Host
| series | src |
|---|---|
| `disk.free_bytes{volume=/,C:,D:}` | **NEW** (WSL: `os.statvfs` on /, /mnt/c, /mnt/d, no Windows process needed) |
| `disk.vhdx_bytes`, `disk.vhdx_slack_bytes` (vhdx − used) | **NEW** (stat of the VHDX path from WSL) |
| `disk.dir_bytes{dir}` for `_artpipe`, `_obs`, `_rmbuild`, `JawaBench/tps/logs`, Saves, `~/.local/state`, seat `/tmp` | **NEW**, hourly (the directory walk is the expensive part) |
| `mem.host_avail_mb`, `mem.commit_pct`, `mem.vmmem_ws_mb` | B sys.memory (and C host when on) |
| `mem.cgroup_current{cgroup}`, `mem.oom_kill{cgroup}`, `mem.psi_some{cgroup}` | C |
| `cpu.host_pct` | **NEW**, cheap in B (GetSystemTimes via ctypes) |

### 3.4 Pipeline
| series | src |
|---|---|
| `artpipe.queue{state}` (pending/active/done/failed) | F dirs |
| `artpipe.jobs_done`, `artpipe.job_s{channel}`, `artpipe.failures`, `artpipe.quota_pct{channel}` | F throughput/registry |
| `review.sheets_live`, `review.unseen_rows` | D read_sheets |
| `ledger.open_items{seat}`, `ledger.needs_owner` | E |

### 3.5 Agents
| series | src |
|---|---|
| `agents.windows{seat,state}`, `agents.subagents{seat}` | D sessions (already computed every 5 s and discarded) |
| `bridge.held{seat}` + hold duration | E bridge events |
| `pulse.alarm_age_s`, `pulse.time_to_notice_s` | D metrics.jsonl |

---

## 4. Storage choice

| option | for | against | verdict |
|---|---|---|---|
| **(a) JSONL only** (what exists) | zero new infra. Every collector already does it, it is crash-safe and greppable | every question needs a bespoke reader; no cross-source join; full-file scans on D: are slow (drvfs) | keep as the **raw layer**, never the query layer |
| **(b) SQLite index over the JSONL** | stdlib (`sqlite3` module 3.46.1 present; the CLI binary is absent, which does not matter); one file, no daemon, no ports; WAL allows concurrent readers; agents query it with a python CLI; rollups are plain SQL; rebuildable from the raw JSONL at any time (it is a cache, so the "derived artifact" rule is met by never committing it) | single-writer (fine: one ingest timer); no built-in dashboards | **RECOMMENDED** |
| **(c) VictoriaMetrics single binary (+ Grafana)** | real TSDB, PromQL, excellent compression, Grafana is the best UI | two more daemons to keep alive across WSL restarts (the `\WSL Keepalive` task already exists for a reason); PromQL is a new language for every agent; push or scrape adapters for 10 bespoke JSONL formats; Grafana on Windows vs WSL port forwarding; does not hold event data (stalls, proof rows) well | not now. Revisit only if (b) hits a wall, and (b)'s ingest can feed it later unchanged |
| **(d) Prometheus + node_exporter** | standard | scrape model fits games badly (the game is not an HTTP target); retention tuning; heavier than (c) | no |

**Recommendation: (b).** Store at `~/.local/state/rm-telemetry/telemetry.db` (ext4, never D:, because drvfs
plus SQLite locking is a known bad pair) with three tables:

- `points(series TEXT, ts REAL, value REAL, labels TEXT, src TEXT)`, index (series, ts)
- `events(ts REAL, kind TEXT, subject TEXT, detail JSON, src TEXT)`, covering stalls, deploys, builds, game state, proof runs, OOM
- `cursors(src_path TEXT PRIMARY KEY, inode, offset, fingerprint)`, so ingest is incremental and idempotent

Rollups go in `points_1m`, `points_1h` (min/avg/max/count), produced by the ingest pass. Retention: raw 14 days,
1m 90 days, 1h forever (≈ a few MB a year). The raw JSONL keeps each source's own retention, and the DB can
always be rebuilt with `telemetry rebuild`.

---

## 5. Collection

| who | where | cadence | what |
|---|---|---|---|
| **existing JawaBench TPS sampler (A)** | in game | 5 s / 60 s | unchanged. Optional expansion: an always-on per-mod attribution bucket is *not* proposed (it was ruled out of the hot path for cost); instead see the scheduled timing below |
| **health_observer (B), made standing** | Windows, pythonw.exe | 5 s | install the scheduled task its docstring already specifies; add `disk.free` (GetDiskFreeSpaceExW) and `cpu.host` sources (ctypes, no console window). This also retires the need for memwatch's `--no-host` path |
| **memwatch (C)** | WSL timer | 1 min | unchanged (`--no-host` stays) |
| **NEW `telemetry ingest`** | WSL systemd user timer `rm-telemetry.timer` | 1 min | tails A, B, C, D, E, F, G, I, K, L by cursor; writes points/events; computes rollups; evaluates alert rules; writes `alerts.json` for pulse. Plus an hourly `disk` sweep (statvfs, VHDX stat, dir sizes with a time budget) |
| **NEW deploy/build events** | `deploy_custom_mods.py --apply`, `winbuild.py`, `modset_builder.py --apply` | per action | one line each to `~/.local/state/rm-telemetry/changes.jsonl`: ts, mod(s), sha, srchash, file count, mod-list digest. About 10 lines per tool |
| **NEW scheduled component timing** (owner choice Q3) | bridge, only when the bridge is free and the game is Playing | e.g. one 600-tick `jawa/map_comp_timing` after each deploy that touched a mod with a MapComponent | persists `game.mapcomp_ms_per_tick{type,mod}` |
| **NEW Player.log error parser** | inside ingest | per archived log + live tail | exception counts by type and mod. It reads A's archive, so the 10k cap and launch overwrite are covered by archival, and a log that hit the cap is marked `capped`, never read as "0 errors" |
| **proof runs** | `validation_core` | per run | emit `obs_events` (I) in validation_core so current runs leave per-call records; ingest G rows as `proof.check` points |

Cost guard: every collector already reports its own cost (B's costUs, A's writer health). Ingest records
`telemetry.ingest_ms` and `telemetry.lag_s{src}` about itself, so a dead source reads as **stale, never as 0**.
This is the project's standing "missing ≠ zero" rule, applied per source.

---

## 6. Surfacing

1. **Agent CLI first** (it is the stated reason: "debugging agents read history instead of re-measuring"):
   ```
   telemetry series [--grep tps]                  what exists, last value, freshness per source
   telemetry query game.tps --since 1h [--every 1m] [--labels map=0]
   telemetry at "yesterday 15:00" --span 10m       every series + event around a moment (generalises tps_record --at)
   telemetry events --kind deploy,stall,oom --since 24h
   telemetry diff game.tick_ms --around deploy:<sha>      before/after with the change event
   telemetry health                                  stale sources, gaps, ingest lag
   ```
   On PATH via `~/.local/bin` like `rimflow`/`modcheck`. Every output names its source and freshness. A
   series with no data in the window prints UNMEASURED.
2. **RimPulse**: pulse_core reads `alerts.json` from ingest and turns breaches into its existing `red`/`amber`
   rows (it already has ack/noise, toast, time-to-notice metrics), so there is no second alert system. The
   widget gains one compact **sparkline strip** (TPS, host avail MB, C:/D:/WSL free, artpipe queue) served from
   a new `/api/series?name=&since=` endpoint on the existing 127.0.0.1:8765 server.
3. **Alert thresholds** (starting values; owner tunes them):
   - disk free < 50 GB on any volume = amber, < 20 GB = red; VHDX slack > 300 GB = amber "compact WSL" (it is about 430 GB now)
   - host commit > 90 % = amber; any oom_kill increment = red (memwatch already toasts; route it through pulse)
   - game tps_ratio < 0.5 for 2 min while unpaused = amber; a `stall` > 10 s = amber; `silence` = red
   - `game.log_capped` during a proof run = amber (the run's log budget is UNMEASURED)
   - a source stale > 3× its cadence while its producer should be up = amber "telemetry blind: <src>"
   - artpipe failures > N in 1 h, or quota_pct > 90
4. **No Grafana in the MVP.** If the owner wants big dashboards later, Grafana's SQLite datasource can read the
   same DB read-only.

---

## 7. Detection

- **Deploy-anchored regression.** For each `deploy` event touching mod M: compare `game.tick_ms` and
  `game.attr_ms{stage}` (and `mapcomp_ms_per_tick` for M's types, when timed) in matched windows. The windows
  are same save, unpaused, same speed multiplier, from N sessions before vs after; A's session manifest
  carries the mod digest, so sessions group by mod set. Flag when the median shift > max(20 %, 3 × MAD of the
  before-windows). Output: an `events` row `regression` with both windows' sizes, plus a pulse amber naming the
  mod and the sha.
- **Change-point on steady series** (heap growth per hour, log bytes/s, disk free slope): a simple
  two-window CUSUM in python. No ML.
- **Proof-check flips**: `proof.check` PASS→FAIL or →UNMEASURED between consecutive runs of the same
  script and mod_hash. Pulse amber with the row id.
- **Disk projection**: linear fit of free bytes over 7 days gives "days until full" per volume. Amber at < 14 days.
- Guardrails, from the project's own lessons: every detector prints its window sizes and a **sanity probe**
  (a known non-regression replayed). A detector with an empty before-window says UNMEASURED and does not report "no change".

---

## 8. Phasing and effort

| phase | content | effort |
|---|---|---|
| **P0: turn on what exists** (≤1 h) | install the health_observer scheduled task (owner choice Q5: it is a Windows task); confirm A's retention; nothing else | 0.5–1 h |
| **P1 MVP** (1 day) | `rm-telemetry` package: schema, cursor ingest for A, B, C, E, F, K; hourly disk sweep (statvfs ×3, VHDX stat, 7 dirs); `changes.jsonl` in deploy/winbuild/modset_builder; CLI `series/query/at/events/health`; `alerts.json` → pulse rows for disk, oom, stale-source; selftest with fake streams | ~6–8 h Sonnet-ladder coding plus a review |
| **P2 game depth** | Player.log exception parser (by mod); G proof rows → `proof.check`; selftest history; `telemetry diff --around deploy`; regression detector on tick_ms | 1–1.5 days |
| **P3 surfacing** | `/api/series` + sparkline strip in the lantern widget; disk projection; proof-flip alerts | 0.5–1 day |
| **P4 bridge depth** | validation_core emits obs_events; scheduled `map_comp_timing` after relevant deploys (bridge-gated, opt-in); `bridge.call_ms` series | 1 day |
| **P5 cleanup** | move proof result JSONs out of git (→ `D:\Luke\dev\_proofs\` or `~/.local/state`, with a committed index of run id + verdict summary); memwatch drops its dormant host code once B is standing | 0.5 day + owner ruling |

Total ≈ 4–5 working days spread out. The MVP alone answers "is the disk filling, is memory short, what was TPS at T, what deployed just before it got slow".

---

## 9. Skill proposal

**Yes, a project skill `telemetry`** in `skills/telemetry/` (repo, symlinked like the others), built in P1
and not before.

- `SKILL.md` trigger: *"before re-measuring anything about the game, host, disk, memory, tests or pipeline; when
  asked 'was it slow at T', 'when did X change', 'is the disk filling'; when adding a new collector or series;
  when an alert fires"*.
- Body: the source map (§1 table, trimmed), the CLI verbs, "query history before you re-measure", the freshness
  rule (stale ≠ 0, missing = UNMEASURED), how to add a series (emit JSONL with ts plus a cursor-ingest adapter;
  never write the DB directly), and the alert-rule file format.
- `references/sources.md`: per-source schema notes (for example: ledger key is `event` not `kind`; TPS
  `sample.attr` triplets; B's per-probe `status`).
- `references/traps.md`: the 10k Verse.Log cap and 1k journal ring (lesson link); `--no-host` and why; drvfs
  plus SQLite; zsh word-splitting in sweeps; a round number of zero is a query bug until proven.
- **Global promotion: partly.** The *pattern* (append-only JSONL per collector + cursor-ingested SQLite + one
  query CLI + "stale is not zero") is project-independent and fits `~/.claude/skills/measuring-large-artifacts`'
  family. I propose a short global skill `local-telemetry-pattern` **only after** P1 has run for two weeks and
  proved itself. Promoting an unbuilt design is how stale doctrine starts.
- **Merge candidates:** `tps_record.md`'s "Answering was it slow at T" section becomes a pointer to `telemetry at`
  once P2 lands. `tps_record.py` stays as the TPS-specific deep reader, and `telemetry at` calls it.

---

## Top 10 actions, ranked by value

| # | target path | action | why | risk if wrong |
|---|---|---|---|---|
| 1 | Windows Task Scheduler `RimMandrake\Health Observer` → `src/RimMandrake/Utils/health_observer.py` | KEEP + turn on (install the task its docstring specifies) | host and game memory series have been dark since 2026-10-10 15:40, and the collector is built and selftested | a pythonw console flash (it is pythonw, so none is expected); verify once with the owner watching |
| 2 | NEW `src/RimMandrake/Utils/telemetry/` + `rm-telemetry.timer` | build P1 (SQLite cursor ingest + CLI + disk sweep) | one query surface; disk finally measured | DB is a rebuildable cache, so a bug costs a rebuild only |
| 3 | `src/RimMandrake/Utils/deploy_custom_mods.py`, `winbuild.py`, `modset_builder.py` | add a `changes.jsonl` line per apply | without change events no regression can be attributed | ~10 lines each; a failed write must never fail the deploy (wrap it) |
| 4 | `C:\Users\Mandrake\AppData\Local\wsl\{dbc3dd4c-…}\ext4.vhdx` | alert on VHDX slack; owner decides on compaction | 975 GB file vs 541 GB used: about 430 GB reclaimable on C: | compaction needs `wsl --shutdown`, which kills every seat. It is the owner's call |
| 5 | `src/RimMandrake/Utils/pulse/pulse_core.py` | read `alerts.json`, emit pulse rows | one alert surface, ack/noise reuse | an extra row type; selftest_pulse covers the classify functions |
| 6 | `src/RimMandrake/Utils/validation_core.py` | emit `rimdrive/obs_events` per bridge call | current proof runs leave no per-call record (newest `_obs` run 2026-10-10) | non-blocking by contract; a dropped event marks the run telemetry-incomplete, never failed |
| 7 | `src/RimMandrake/*/northstar/*.json` (218 tracked, 98.1 MB) | MOVE out of git to an outside-git store + committed summary index | derived artifacts in git (rule in `~/.claude/CLAUDE.md`); the repo grows ~0.5 MB per run | proof scripts and docs that cite a result path must be repointed; needs an owner ruling (Q4) |
| 8 | NEW Player.log exception parser over `JawaBench\tps\logs` | build (P2) | errors-by-mod as a series, with cap and overwrite already handled by A's archive | attribution by namespace can misassign. Label it "lead, not verdict" as map_comp_timing does |
| 9 | `skills/telemetry/` | create after P1 | stops agents re-measuring | skill written before the tool exists would rot |
| 10 | `src/RimMandrake/Utils/memwatch.py` host block + `rm-memwatch.service --no-host` | DELETE the host path once #1 has run a week | dead code; B supersedes it without a console window | none if B is standing; keep until it is |

## Questions only the owner can answer

1. **Storage.** (a) SQLite cache over the existing JSONL, recommended: no daemon, agents query by CLI. (b)
   VictoriaMetrics + Grafana: prettier dashboards, two more daemons to keep alive. (c) JSONL only plus a
   query CLI: no DB at all, slower queries.
2. **Where you look.** (a) a sparkline strip in the Lantern widget only. (b) the strip plus a full-page
   dashboard on the pulse server (127.0.0.1:8765/telemetry). (c) no visuals: alerts in pulse rows, history via
   agents.
3. **In-game sampler scope.** (a) leave the TPS record as is: per-component timing stays on demand. (b) the
   bridge automatically runs a 600-tick component timing after each deploy that touched a mod with a
   MapComponent, only when the bridge is free. (c) an always-on per-mod attribution bucket in the sampler (it
   costs main-thread time every tick, and was ruled out of the hot path before).
4. **Proof result JSONs in git (218 files, 98 MB).** (a) move them outside git and commit only a summary index.
   (b) keep the last N per mod in git, older ones moved out. (c) leave as is.
5. **Windows-side collector.** (a) install the health_observer scheduled task (every 5 min re-start, lock makes it
   single-instance). (b) have the Lantern widget, already running, host those probes instead. (c) neither: accept
   no host series.
6. **Cadence / retention.** (a) raw 14 days, 1-min rollup 90 days, hourly forever (recommended, a few MB). (b) raw 7
   days, hourly 1 year. (c) keep everything raw forever.
7. **WSL VHDX slack (≈430 GB on C:).** (a) alert only. (b) alert plus a monthly compaction you schedule (needs
   `wsl --shutdown`, which ends all seats). (c) ignore while C: is at 44 %.
