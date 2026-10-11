# 08: Telemetry deep design: SQLite / RimPulse / VictoriaMetrics / Grafana (2026-10-11)

*Design only. Nothing here is built. It builds on `06_telemetry_design.md` (first pass) and `07_rimflow_rimpulse.md` §5
(RimPulse interfaces), and corrects both where the code says otherwise.*

## 0. Owner's brief and headline

Owner (typed, on the card): *"Do a deep design pass for SQLite, RimPulse, VictoriaMetrics, Grafana... and I don't think
1/min frequency will capture everything we need to know while Bridge is supporting a real live test at speed 3 in the
game, though that's ok for external metrics like disk space and memory. Look at ALL the bridge metrics it's dumping out
plus the external monitors we do (or should) look at here. There's other reports generated on this topic to consider too."*

**Headline, in six lines.**
1. **He is right about 1/min.** "Speed 3" is Superfast: the engine's target is 360 TPS, or 720 when nothing is happening
   (decompiled `TickManager.TickRateMultiplier`: 6 / 12). The measured full list runs **~17 TPS** at that speed
   (median of 134 run windows, `tickMs` 55). One minute is 1,000 to 43,000 ticks, so a 1/min point averages away every
   spike, burst and stall. A per-tick error at 360 TPS **fills the 10,000-message Verse.Log cap in about 28 s**, after
   which Player.log goes blind.
2. **The game side already has the right engine.** The TPS record (`JawaBenchTps*.cs`) has a non-blocking, bounded,
   drop-counting background writer, 5 s windows, a 2 s stall detector and a watchdog thread. **Do not build a second
   one.** Extend it with a *test tier*: 1 s windows, a per-window tick-duration histogram, a per-tick "flight recorder"
   ring dumped on incidents, and an exception counter hooked *ahead* of the log cap.
3. **Storage: hybrid.** Raw JSONL stays the record of truth (it already is). **VictoriaMetrics** on the Windows side,
   on a data SSD, holds numeric series. **SQLite** in WSL holds events, test runs and proof rows. **Grafana**
   draws from both for the owner, and a `telemetry` CLI serves agents. RimPulse stays the alert surface and never
   becomes a store.
4. **Rejected:** Prometheus (a pull model fits a game process badly, and VictoriaMetrics accepts the same queries at a
   fraction of the cost). RimPulse as the store (unversioned, per-machine, no numeric field). DuckDB/Parquet as a store:
   it is kept as an optional *analysis* tool over SQLite and JSONL, not a third database.
5. **The biggest gaps are not storage.** There are no deploy or build events, the current proof path does not record
   bridge calls, and the health observer is not installed as a standing task. Those come first (P0/P1).
6. **MVP ≈ 2 days:** P0 (turn on), P1 (VictoriaMetrics + ingest + `telemetry` CLI + change events), with the
   in-game test tier as P2.

---

## 1. Source census (read from code)

### 1.1 In-game / bridge side (the JawaBench companion, inside RimWorld)

All rows land in `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\tps_<utc>_<session>_<pid>_<seg>.jsonl`
through one writer (`JawaBenchTpsWriter.cs`): a background thread (`BelowNormal` priority), a bounded queue of
`QueueCapacity` 4,096 lines with `CriticalReserve` 512 for non-bulk rows, a full line **dropped and counted, never
blocking the game** (`wdrop`, `wdropCrit`, later a `dropped` row with seq range), commit-aware retry, torn-tail repair,
2 MB segments. Retention comes from `tps_settings.json`: 7 days / 256 MB for records, 1 GB for archived Player.logs.
Every row carries an envelope `seq, v, utc, mono, session, kind`.

**MEASURED 2026-10-11 (python over all 21 segments, 12.38 MB, 2026-10-10T15:30Z to 2026-10-11T16:26Z):**

| kind | rows | avg bytes | native rate | what it carries (fields read from the code) |
|---|---|---|---|---|
| `sample` | 11,463 | 1,039 | 1 per 5 s real time (`CadenceSeconds`) | window maths (`JawaBenchTpsMath.WindowFields`): `state` (run/paused/mixed/stall/longevent), `dReal, dTicks, ratio, tps, tpsWall, target, expected(Lo), runS, pausedS, explainedS, stallS, ambigS, multMin/Max, mult, transitions, frames, fps, gapMaxMs, gaps, simMs, simMaxMs`; then `game, speed, tg, tickMs` (engine `MeanTickTime`), `focused, gc` (gen-0 count), `heapMB`; then the profiler's `attr{stage:[count,totalMs,maxMs]}` for 10 coarse stages (`tick, tl:Normal/Rare/Long, world, worldPost, mapPre, mapPost, mapComp, gameComp`), `top`, `worst[]` (up to 3 ticks ≥ 30 ms with exclusive stage split), `attrValid, profSkipped, profHooks, profEstMs`; writer health `wq, wfly, wdrop, wdropCrit, werr, wtorn` |
| `context` | 1,014 | 313 | every 60 s | per map (≤ 8): `id, size, biome, pawns, things, current`; `mapCount, worldPawns` (O(1) private HashSet counts), `heapMB, workingSetMB, save` |
| `incident` | 46 | 560 | event: frame gap > 2 s | `stall`/`longevent`, `gapS, explainedS, unexplainedS, quietPhase, phase, prevSimS, gcDelta`, save state, ticks, speed, heap |
| `silence` / `resumed` | 33 / 26 | 357 / 162 | watchdog thread: main thread silent > 10 s, repeat every 30 s | `silentS`, context fields, `phase` |
| `session` | 19 | 1,042 | per launch | pid, startedBy, build, mod digest, settings note |
| `game` / `menu` / `save` | 121 / 54 / 83 | ~170 | event | game seq, save name; program state; save file and `saveS` |
| `marker` | 154 | 139 | event (a bridge-written `why`) | the existing hook for test annotations |
| `awareness` | 6 (+33 mis-keyed, below) | 617 | event, only while ARMED (TTL 30 min) | incident journal, pawn origin (arrival, generation, spawn chain) |
| `log` | 10 | 478 | per launch | Player.log archived to `tps\logs\` with sha256 |
| `shutdown(-complete)`, `error` | 4, few | | event | |

⚠️ **Defect found while measuring:** awareness rows carry their own `"kind":"<PawnKindDef>"` field *after* the
envelope's `"kind":"awareness"`. JSON readers keep the last duplicate key, so 33 rows read as kind `Tribal_Warrior`,
`Colonist`, `Megaspider` and so on (`JawaBenchAwareness.cs:438`). Any `kind == "awareness"` filter misses them. The fix
is to rename the field to `pawnKind`. File it as an item; this design does not fix it.

**Measured speeds** (run-state windows only):

| `mult` | windows | TPS p10 / median / p90 / max | `tickMs` median | reading |
|---|---|---|---|---|
| 1 (Normal) | 332 | 8.8 / 55.7 / 60.0 / 66 | 6.9 | |
| 3 (Fast) | 37 | 11.1 / 18.1 / 145 / 153 | 36.8 | |
| 6 (Superfast, "speed 3") | 134 | 9.1 / **16.8** / 21.2 / 162 | **55.5** | full list is CPU-bound: ratio ≈ 0.05 |
| 150 (Ultrafast, dev, nothing happening) | 75 | 8.7 / 11.4 / 3,333 / 3,829 | 93.6 | the high tail is the minimal list |

The worst single ticks: 1,110 recorded ≥ 30 ms, median 153 ms, p99 597 ms, max 1,120 ms. Writer drops: **0**. The
existing queue has never overflowed at 5 s cadence.

**Other in-game instruments (read from the code), all on-demand bridge `[Tool]`s with no persistence:**

| tool | file | returns | persisted? |
|---|---|---|---|
| `jawa/tps_report` | `JawaBenchTpsSampler.cs` | the in-memory ring (`RingCapacity` 720 × 5 s = last hour) + writer health + sustained-low verdict | no, but the same rows are on disk |
| `jawa/map_comp_timing` | `JawaBenchMapCompTiming.cs:64` | per-MapComponent type: calls, total ms, ms/tick, max, owning mod, over N real ticks; patches and then unpatches | **no: lives in prose** (the 0.152 → 0.024 ms/tick hose figure) |
| `jawa/time_perf` | `JawaBenchResearchTimeTools.cs:654` | `MeanTickTime, TicksThisFrame, TickRateMultiplier, curTimeSpeed` | no |
| `jawa/load_stall_probe` | `JawaBenchLoadStallProbe.cs` | racy snapshot of `LongEventHandler` state during a cold-load hang (deliberately not marshalled to the main thread) | no |
| `jawa/awareness`, `jawa/incident_journal` | `JawaBenchAwareness*.cs` | capped in-memory stores; per-hook cost metering | only `aware.disk-rows` while armed |
| `jawa/pawn_census`, `jawa/wealth_recount`, `jawa/pawn_health`, `jawa/pawn_memory` | various | counts | no |
| `jawa/tps_test_block`, `jawa/tps_test_attribution` | TPS test tools | synthetic load for the A/B | no |
| `LoadTracer` mod | `src/RimMandrake/LoadTracer/` | per-`[StaticConstructorOnStartup]` lines in Player.log during cold load | Player.log only |

**The bridge's own records:** RimBridge keeps a **1,000-entry log journal ring** (all levels).
`validation_core.py:153` `LogTap` polls it after every tick step and counts entries lost to scroll-off. Per-call timing
and `bridge_calls.jsonl` are covered in §1.2.

**Two engine facts this design rests on (RimSage, decompiled 1.6, read 2026-10-11):**
- `TickManager.TickRateMultiplier`: Fast 3; Superfast **6**, or **12** when nothing is happening; Ultrafast 15, or 150.
  The engine caps ticks per frame at 2 × mult and stops ticking after 45.45 ms of tick work per frame
  (`FrameBudgetSeconds`).
- `Verse.Log.Error(string)` checks `if (PreventLogging) return;` **inside its own body**, and the vanilla call already
  pays `StackTraceUtility.ExtractStackTrace()`. So a **Harmony prefix on `Log.Error`/`Log.Warning`/`Log.Message` sees
  every call, including the ones the 10,000-message cap suppresses.** This narrows the GPT review's "log cap is a blind
  spot" (`Transient/foundry_metrics_combined_20261010.md` §3), which was about the threaded Unity log event. Only direct
  `UnityEngine.Debug.LogError` calls and unhandled Unity exceptions stay invisible after the cap.

### 1.2 External monitors (outside the game process)

Read from the code and checked against `systemctl --user` and file mtimes, 2026-10-11 ~09:27 PDT.
`$U` = `src/RimMandrake/Utils`.

| collector | writer | fields | native rate | lands at | retention | state |
|---|---|---|---|---|---|---|
| **bridge call evidence** | `$U/rimbridge_client.py:174 _evidence` (calls at :257, :685, :699, :718) | start `{ev,cid,tool,args_sha256,client,endpoint,mutating,os,pid,run,script,seat,t}`; end `{ev,cid,status,success,ms,t}`; reconciled `{ev,cid,as,note}` | per bridge call | `D:\Luke\dev\_rmscratch\bridge_calls.jsonl` + `.1`; in-flight markers in `bridge_inflight\` | rotates at 20 MB, keeping one `.1` (`:157`) | LIVE. **MEASURED:** 144,224 lines = 72,110 completed calls, all from **2026-10-11 05:21Z to 15:17Z**. ⇒ **retention is about 10 hours**, not days. Latency p50 48 ms, p90 82, p99 1,052, max 146 s. 253 active minutes, median **234 calls/min**, max **1,359/min** (~23/s). Top tool `jawa/mod_settings_field` 52,849 calls |
| bridge sessions | `rimbridge_client.py:125` | `{started,finished,seconds,calls,client,script}` | per client session | `_rmscratch\bridge_sessions.jsonl` | none | idle since 10-10 |
| obs_events | `$U/rimdrive/obs_events.py:65` | `{v,run_id,producer,seq,t,mono,ev}`; `call_end` adds `latency_ms, outcome, timeout, transport`; `run_end` adds emitted/dropped/written | per call (queue 20,000, drops counted) | `D:\Luke\dev\_obs\runs\<run>.jsonl` (44 files, 111 MB) | none | DORMANT since 10-10. **A second per-call recorder** that duplicates bridge_calls. `validation_core.py` (the live proof path) does not emit it |
| LogTap | `$U/validation_core.py:152-215` | keeps warn/error/exception journal entries, `lost`, `gaps`, `polls`; a sentinel for the 10k cap | after each `step_game_ticks` and block boundary | in memory, then the proof JSON | via proof JSON | LIVE inside proofs |
| health_observer | `$U/health_observer.py:707` (rows), `:636`/`:726` start/stop | `{v,kind(start/sample/event/error/stop),utc,mono,sources{…}}`; 8 sources: `obs.heartbeat, game.identity, game.cpu, game.mainthread, game.memory, sys.memory, log.growth, log.milestones`, each with `costUs` | **5 s** while a RimWorld process exists, 30 s otherwise (`:951`) | `…\JawaBench\health\observer_<utc>_<pid>_<seg>.jsonl` | 4 MB segments, 14 d, 256 MB (`:37-40`) | **DORMANT** since 10-10 15:40. No scheduled task (left off on purpose until MUST 17, per `design/RimMandrake/game_health_record.md` l.173) |
| tps_observer | `$U/tps_observer.py` | finds silent / heartbeat-stale-but-alive / exited-without-shutdown games; writes `observer.jsonl`, `observer_last.json` | 2 min | `…\JawaBench\tps\` | — | LIVE (Windows task "RimMandrake\TPS Observer", pythonw) |
| memwatch | `$U/memwatch.py:397-411`, `rm-memwatch.timer` | samples `{ts, cgroups{name:{events{high,max,oom,oom_kill}, current, peak, max, swap, stat{anon,file,shmem,dirty,writeback}, psi{some_avg10,full_avg10}}}}`; events `{ts,kind,cgroup,seat,delta,total,toast,snapshot}` | 1 min | `~/.local/state/rm-memwatch/` | samples rotate at 20 MB (one `.1`); **events unbounded** | LIVE, `--no-host` (host memory dark from WSL by design) |
| objstore sampler | `$U/scratch_clone.py:330`, `rm-objstore.timer` | store bytes/objects, borrowers, fsck, **`disk_free_bytes`** (WSL root only) | 1 h | `~/.local/state/rm-objstore/samples.jsonl` | none | LIVE, 74 rows. The only disk series that exists |
| RimPulse | `$U/pulse/pulse.py:82`, `rm-pulse.service` (+ `-health` 2 min, `-digest` 06:00/17:30) | `pulse.jsonl` row transitions `{key,kind,was,ts}`; `metrics.jsonl` `{m: alarm_open/close/ack, toast, digest…}`; `pulse_now.json` | 5 s collector; rows on change | `~/.local/state/rm-dashboard/` | none | LIVE. HTTP `127.0.0.1:8765`: GET `/api/now`, `/api/stream` (SSE), `/api/thumb`; POST `/api/ack`, `/api/seen`, `/api/probe`, `/api/metric` |
| rimflow ledger | `rimflow/cli.py:2176-2288` (bridge), `./game` → `broadcast.py` → `rimflow game` | bridge `{seat,event:"bridge",state:taken/released,purpose,override,ts}`; game `{seat:"OWNER",event:"game",state:UP/DOWN/LOADING,ranBy,ts}` | per action | `infrastructure/state/ledger/events/<SEAT>.jsonl` (git) | forever | LIVE: already the authority for game state and bridge holds |
| artpipe | `$U/artpipe/common.py:510` (throughput), `artreg.py:132` (registry) | throughput `{id,channel,model,status,elapsed_s,cost_usd,daemon_attempts,meter_before/after,ts}`; registry `{event,job_id,target,verdict,ts}` | per job | `D:\Luke\dev\_artpipe\` | none | LIVE (idle since 03:07); `art_status.json` STALE since 10-02 |
| selftests | `$U/run_selftests.py:856` | `last_run.json` (wall, results) + compressed records | per run | `~/.local/state/rm-selftests/` (316 MB) | last run only; run-caches accumulate | LIVE, no history |
| codebase health | `codebase_health_publish.py:313`, `rm-codebase-health.timer` | snapshot | 15 min | `infrastructure/state/codebase_health_last.json` | overwrite | LIVE, not a series |
| proof results | `src/RimMandrake/*/northstar/*.json` | `rows[]{id,status,class,detail,block}`, `wall_s, mod_hash, log_revive, control_noise, env` | per run | in git (218 tracked, 98 MB per 06) | forever | LIVE, not a series |
| deploy / build / mod-list | `deploy_custom_mods.py --apply`, `winbuild.py`, `modset_builder.py --apply` | **nothing written** | — | — | — | **GAP** |

**Disks the store can live on** (PowerShell `Get-Partition` → `Get-Disk`, measured):

| letter | physical | size | used | role today |
|---|---|---|---|---|
| C: | disk1 Kingston SFYRD4000G **NVMe** | 3.7 TB | 1.6 TB | OS, RimWorld, **the 908–975 GB WSL VHDX** |
| D: | disk2 Kingston NVMe | 3.7 TB | 1.9 TB | `D:\Luke\dev`, `_artpipe`, `_rmscratch`, `_obs` |
| **E:** | disk3 Kingston **NVMe** | 3.7 TB | **269 MB (empty)** | nothing |
| F: | disk0 WDC WD142KFGX **SATA HDD** | 13 TB | 560 MB (empty) | nothing: an archive tier |
| G: | not a local partition (it is in `Get-PSDrive` but not in `Get-Partition`; probably a cloud drive) | | | not for telemetry |

### 1.3 Other reports on this topic (what each already concluded)

| doc | date | built? | conclusion that binds this design |
|---|---|---|---|
| `design/RimMandrake/tps_record.md` | 10-10 | built | TPS is a standing record. Judge `ratio`, never raw TPS against 60: *"170 TPS is healthy at speed 3 and dire at speed 4"*. Stall = frame gap > 2 s, silence > 10 s. MUST 17 (full-list overhead) is still owed |
| `design/RimMandrake/game_health_record.md` | 10-10 | mixed | Owner ruled **"Everything at once"** (card) as option F, evidence-first. **"Every metric must be evaluable and removable later"**: stable id, switch, measured cost, a metrics ledger (`HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP`). **Recorder budget: campaign profile 10 %, test profile 100 %** (owner, 2026-10-10). Seven binding rules: unavailable ≠ 0; no automatic mod blame; process counters never reset at game change; **merge histograms, never average p99s**; bulk goes in separate capped files; label coincidences; the 10k log cap |
| `Transient/foundry_metrics_combined_20261010.md` (+ design, GPT review, build log) | 10-10 | partial | Tiers: cheap always-on, triggered, on-demand deep, external observer. The in-process watchdog is blind during GC, so an external observer is required. Missing metrics named there: **tick-duration histogram, bridge queue latency and main-thread occupancy**, per-map sim cost. None heavier goes always-on before MUST 17 |
| `Transient/foundry_tps_must17_20261010.md` | 10-10 | measured | The full-list load failed at ~33 min, so MUST 17 has no full-list figure. A 67-mod A/B at Superfast showed attribution on/off inside ±4 % noise. Profiler estimate 0.0004 ms/tick |
| `Transient/foundry_tps_diagnose_20261010.md`, `design/RimMandrake/huge_footprints_perf.md` | 10-10 | measured, fixed | Rot map 93.6 ms/tick (~8 TPS). `MapComponent_HugeFootprints` 70 ms/tick, found by `jawa/map_comp_timing`, fixed `f3774dd15`. GC every 4.7 s on a ~5 GB heap, not the cause. **This is the case the design must make routine**: a coarse stage dominating, then on-demand per-component timing, then a persisted number |
| `Transient/live_sheet_check_2026-10-10/low_tps_2026-10-10.md` | 10-10 | not reproduced | 12.3 TPS on one quicktest map against 55–59 elsewhere. 100–900 ms single-tick spikes. **Cause never identified**: the "was it slow at T, and why" question the per-tick flight recorder answers |
| `design/RimMandrake/bridge_validation_observatory.md` | 10-03 | draft | Coverage-of-required-checks plus bridge time, from deterministic JSONL events. Its emitter (`obs_events`) is dormant |
| `Transient/away_dashboard_design_2026-10-08.md`, `pulse_rimflow_tie_2026-10-10.md` | 10-08/10 | built | RimPulse is the attention surface (5 s collector, ~80 ms ledger read) |
| `Transient/weekly_cleaning_2026-10-11/06_telemetry_design.md` | 10-11 | design | SQLite-in-WSL index, 1-min ingest, no Grafana. **Revised here**: see §4–5 for why the store moves to Windows and gains VictoriaMetrics |
| `Transient/weekly_cleaning_2026-10-11/05_git_and_disk.md` §7a | 10-11 | design | Disk watch as a memwatch extension. **Revised here**: the Windows-side collector reads every volume and the VHDX natively, without the PowerShell focus-steal that forced memwatch to `--no-host` |
| `07_rimflow_rimpulse.md` §5 | 10-11 | design | Writers own their JSONL; RimPulse reads, thresholds onto `red`/`amber`, never the store of record; add `/api/series`. **Adopted** |

No doc or ruling chooses Grafana, VictoriaMetrics, Prometheus or SQLite. The storage choice is open.

---

## 2. Rate tiers

**What a resolution must catch, at speed 3:**

| phenomenon | duration / shape | ticks it spans at 17 TPS (full list) | at 360 TPS (target) | resolution that catches it |
|---|---|---|---|---|
| frame stall / long event | ≥ 2 s gap | — | — | **event** (already: `incident`) |
| main thread hung | ≥ 10 s | — | — | **watchdog thread** (already: `silence`) |
| single slow tick (the 100–900 ms spikes) | 1 tick | 1 | 1 | **per tick**, in memory; kept only on trigger (flight recorder) |
| per-component spike | 1–50 ticks | 1–50 | 1–50 | per-tick stage split in the ring; per-window `worst[]` keeps 3 |
| exception storm | 1 per tick or more | 17+/s: 10k cap in ~10 min | **360+/s: 10k cap in ~28 s** | **event counter ahead of the cap**, per window |
| TPS dip / speed drop | 5–60 s | 85–1,000 | 1,800–21,600 | 1 s window in test, 5 s otherwise |
| GC pressure | GC every ~4.7 s (measured) | | | gen-0 count per 1 s window |
| heap / pawn / thing growth | minutes | | | 10 s (test) / 60 s context |
| bridge occupancy | per call (median 48 ms, up to 23 calls/s) | | | per call (already in bridge_calls), aggregated per window |
| host memory, commit, disk, VHDX | minutes to days | | | **1 min** (owner: *"that's ok for external metrics like disk space and memory"*) |

**The tiers:**

| tier | resolution | where computed | where it lands | when on |
|---|---|---|---|---|
| **T0 per tick** | every tick | main thread, existing tick hook, O(1), no allocation | in-memory ring (§3); disk **only** on a trigger | test tier armed |
| **T1 fast window** | **1 s** windows: full `sample` row + histogram + exceptions + bridge occupancy | main thread closes the window; writer thread writes | TPS record JSONL | test tier armed |
| **T2 window** | 5 s (unchanged) | as today | TPS record JSONL | always (campaign budget 10 %) |
| **T3 context** | 10 s in test, 60 s otherwise | as today | TPS record JSONL | always |
| **TE events** | as they happen | hooks | TPS record JSONL (+ capped side files for bulk) | always; side files in test |
| **TX external, fast** | 5 s while the game runs | `health_observer` (Windows) | health JSONL | game up |
| **TH host** | 1 min; directory sizes 1 h | Windows collector + memwatch | collector → store | always |

Speed-3 volume, T1: 1 row/s × ~1.6 KB = **~140 MB per day of armed testing**, raw, before compression. T2 is unchanged at
~1 KB / 5 s ≈ 17 MB per day of play.

---

## 3. In-game ring buffer and flush design

**Principle: the game never waits on IO, and nothing new gets its own thread or writer.** Everything rides
`JawaBenchTpsWriter`'s existing bounded queue (4,096 lines, 512 critical, drop-and-count, background `BelowNormal`
thread, commit-aware retry). The writer already met 0 drops at 5 s; T1 multiplies the bulk rate by 5, which is still
~1 line/s.

### 3.1 Per tick (T0), main thread

Inside the profiler's existing `TickBegin`/`TickEnd` (`JawaBenchTpsStages.cs`), which already snapshots stage totals
per tick:

1. **Histogram increment**: tick duration → one of 28 fixed log-spaced buckets (0.25 ms … 4 s, `histV:1` carried with
   the data, per rule 4). One array increment.
2. **Flight-recorder ring**: a preallocated struct-of-arrays ring of the last **8,192 ticks** (at 17 TPS that is 8 min;
   at 360 TPS, 23 s). Per tick: `tg` (int), `durUs` (int), the 10 exclusive stage deltas in µs (10 ints), gen-0 GC count
   delta (byte), log error/warn count delta (short). ≈ 52 B/tick ⇒ **≈ 420 KB**, allocated once.
3. Nothing else. No strings, no allocation, no locks (single-writer, main thread).

Estimated cost: tens of ns per tick, so under 0.4 ms per real second even at 3,800 TPS. **UNMEASURED** until the MUST 17
protocol runs with the tier armed. That measurement is a gate for P2, not a formality.

### 3.2 Per window (T1 1 s / T2 5 s), main thread closes, writer writes

The existing `sample` row gains:

- `hist`: sparse bucket counts for this window, plus `histV`.
- `exc`: `{"n":total,"sup":suppressedByCap,"top":[[sig,count],…5]}` from the log counter (§3.4).
- `br`: bridge occupancy: `{"calls":n,"mainMs":x,"qMaxMs":y}`, measured where JawaBench tool bodies run on the main
  thread (the owed `tps.bridge-occupancy` metric).
- `tier`: `"test"` or `"campaign"`, so readers never mix 1 s and 5 s windows (rule: keep each band's own interval).

### 3.3 Flight-recorder dump (event-driven)

Triggers: an `incident` (gap > 2 s); a single tick > 250 ms; an exception burst (> 50 in one window); a bridge
`jawa/telemetry_mark dump=true`; test-tier disarm. On trigger the main thread copies the ring (one `Array.Copy`,
~100 µs) into a pooled buffer and hands it to the writer, which writes **a separate capped file**
`…\JawaBench\tps\flight\flight_<session>_<seq>.jsonl.gz` (rule 5) and a reference row `kind:"flight"` in the main
stream. Rate limit: one dump per 30 s; directory cap 1 GB, oldest first. This is what answers
`low_tps_2026-10-10.md`'s "100–900 ms single-tick spikes, cause never identified": each spike comes with the preceding
8,192 ticks' stage split.

### 3.4 Exception counter (event-driven, ahead of the cap)

A Harmony **prefix** on `Verse.Log.Error`, `Log.Warning`, `Log.ErrorOnce`, `Log.Message`. It runs before the method's
own `if (PreventLogging) return;`, so it sees calls the 10,000-message cap suppresses (§1.1). It computes a signature
(first 160 chars, digits → `#`, plus `ErrorOnce`'s key when present) and increments a per-window dictionary capped at
64 signatures (an overflow bucket counts the rest). **First sight of a signature per session** queues the full
message with the stack vanilla already extracted (truncated to 4 KB) to `…\tps\exc\exc_<session>.jsonl`, capped at
64 MB. The window's `exc.sup` counts calls made while `PreventLogging` was true, so a capped log reads **"N errors
suppressed"** rather than "0 errors". Still blind: direct `UnityEngine.Debug.LogError` and unhandled Unity exceptions
after the cap. The reader must say so (rule 1). Attribution to a mod stays a **lead, not a verdict** (rule 2): the
signature, plus the top non-Verse stack frame's assembly, as a candidate.

### 3.5 Arming the test tier

A bridge tool `jawa/telemetry_tier tier=test ttl_min=60` (TTL capped at 240, like awareness's arm) switches T0/T1 and
the side files on, writes `marker` rows at arm and disarm, and falls back to campaign at TTL. A companion profile of
`test` may arm it at launch. **Campaign profile never runs T0/T1**: that respects the owner's 10 % campaign budget until
it is measured. Each piece has its own switch in `tps_settings.json` (`histogram`, `flight`, `excCounter`,
`bridgeOccupancy`) and a row in the metrics ledger, per *"every metric must be evaluable and removable later"*.

### 3.6 Per-component depth (on demand, now persisted)

`jawa/map_comp_timing` stays on demand: per-component timing is ruled out of the always-on path (header of
`JawaBenchMapCompTiming.cs`). Its reply now also goes to the writer as a `kind:"mapcomp"` row (type, mod, ms/tick,
calls, max, ticks spanned), so the number stops living in prose. The test harness calls it automatically whenever a
window's `top` is `mapComp` above a threshold (opt-in; owner question 6).

---

## 4. Storage trade study

### 4.1 Constraints measured here (they decide more than the feature lists do)

1. **WSL2 is NAT mode.** WSL cannot reach Windows `localhost` (that is why `rimbridge_client.py` runs under `python.exe`),
   but Windows *can* reach WSL `localhost` (default `localhostForwarding`; Lantern already POSTs to pulse on 8765).
2. **WSL dies as a unit.** `wsl --shutdown` (VHDX compaction, `.wslconfig` changes, OOM) stops every WSL daemon. Disk and
   memory telemetry matter most at exactly those moments.
3. **The VHDX only grows** (908–975 GB file against 541 GB used, per 05/06). A store inside WSL adds to it.
4. **SQLite over drvfs (`/mnt/*`) locking is unsafe**, so a SQLite file must have its readers and writer on the same side.
5. **Most high-rate producers are Windows-side already**: the TPS record (C:), health_observer (C:), bridge_calls (D:),
   artpipe (D:). WSL-side producers are all ≤ 1/min (memwatch, objstore, ledger, pulse transitions).
6. **E: is an empty 3.7 TB NVMe; F: an empty 13 TB HDD.**
7. **Volume at the rates in §2** (VictoriaMetrics stores roughly 0.4–1 byte per sample; ESTIMATE from its published
   figures, to be measured in P1): test tier ~150 series at 1 Hz ≈ 13 M samples per day of testing ≈ **≤ 13 MB/day**;
   campaign 5 s ≈ 2 MB/day; host 1/min ~300 series ≈ 0.4 MB/day; bridge aggregates per 10 s ≈ 1 MB/day. **Under
   ~20 MB/day worst case, ≤ ~7 GB/year.** Raw JSONL gzipped (≈ 10×) ≈ 15 MB per test-day. **Disk is not a criterion
   that separates the options; ingest model, query, survival and maintenance are.**

### 4.2 Scored table (5 = best; stores and the UI scored separately)

| option | high-rate ingest | agent query (CLI) | owner dashboards | survives WSL restart | maintenance (5 = least) | disk at our rates | fits events / test runs | **total /35** | verdict |
|---|---|---|---|---|---|---|---|---|---|
| **VictoriaMetrics single binary, Windows, data on E:** | 5: push (Influx line, Prometheus text, JSON import), 100 k+ samples/s on one core | 4: HTTP + MetricsQL; agents go through `python.exe` or a thin CLI | 5: native Grafana datasource | 5 | 4: one binary, one data dir, `-retentionPeriod`; downsampling is Enterprise-only, unneeded at these volumes | 5 | 2: events as labelled 0/1 series only; no row detail | **30** | **YES: numeric series** |
| **SQLite (WAL, one writer), Windows-side file on E:** | 3: thousands of rows/s batched; fine for events and runs, wrong for 150 series × 1 Hz forever | 5: SQL from python; agents know it | 3: Grafana SQLite plugin (`frser-sqlite-datasource`), native reads on the same side | 5 | 5: stdlib; a rebuildable cache | 5 | 5: events, runs, proof rows, per-call rows | **31** | **YES: events and test runs** |
| SQLite in WSL ext4 (06's plan) | 3 | 5 | 2: Windows Grafana cannot safely open it; a WSL Grafana dies with WSL | **1** | 5 | 4: grows the VHDX | 5 | 25 | no: dies at the moment that matters |
| RimPulse as the store | 1: 5 s collector, no numeric field | 2 | 2: widget only | 1 | 3 | 3: unbounded files | 1 | 13 | no: keep it the alert surface (07 §5) |
| Prometheus | 2: pull only; a game is not a scrape target, so it needs an exporter or pushgateway | 4 | 5 | 5 | 2: config, retention tuning, more disk per sample | 3 | 1 | 22 | no: VictoriaMetrics accepts the same PromQL with push and less disk |
| DuckDB / Parquet | 2: batch, not streaming | 5: SQL over JSONL/Parquet directly, superb for "compare these 40 runs" | 2 | 5 | 4: a pip install (not present now) | 5 | 4 | 27 | **as an analysis tool, not a store**: P4 optional, reads the raw JSONL and the SQLite file |
| Plain JSONL (today) | 4: append, already done by every writer | 1: a bespoke reader per stream | 1 | per writer | 5 | 2: several are unbounded, bridge_calls keeps ~10 h | 3 | 16 | **keep as the raw layer and the record of truth**, never the query layer |

| UI option | live test view | history and annotations | alerts | maintenance | verdict |
|---|---|---|---|---|---|
| **Grafana (Windows service, localhost:3000)** | 5: 1 s refresh over VictoriaMetrics | 5: annotations from SQLite events | 3: could alert, but would duplicate pulse | 3: one service, provisioned dashboards as files in git | **YES, for looking into things** |
| RimPulse / Lantern | 2: 5 s collector | 1 | 5: ack, time-to-notice, digest, toasts already built | 5 | **YES, for attention**: red/amber rows plus a few sparklines |
| Published artifact pages | 1 | 3 | 1 | 4 | for one-off reports only |

---

## 5. Recommended architecture

```
                       WINDOWS (survives wsl --shutdown)                                   WSL (ext4)
 RimWorld ─ JawaBench writer ─► C:\…\JawaBench\tps\*.jsonl ─┐
            (T0 ring, T1/T2 windows,  + flight\  exc\       │
             events; never blocks)                          │
 health_observer (5 s) ─────────► C:\…\JawaBench\health\ ───┤
 rimbridge_client ──────────────► D:\…\_rmscratch\bridge_calls.jsonl ┤
 artpipe ───────────────────────► D:\Luke\dev\_artpipe\*.jsonl ─────┤      memwatch, objstore, ledger,
                                                            │      pulse.jsonl, selftests
                     ┌──────────── telemetryd (pythonw, scheduled task at logon, restart on failure) ◄── reads \\wsl.localhost\… by cursor
                     │  · cursor-tails every source (1 s while a test tier is armed, 15 s otherwise)
                     │  · samples C: D: E: F: free, VHDX size, dir sizes (1 min / 1 h), natively, no PowerShell
                     │  · hashes ModsConfig.xml + Mods\*\About|Assemblies mtimes: detects deploys even when no tool reports one
                     │  · evaluates alert rules
                     ▼
     E:\telemetry\vm\        VictoriaMetrics (127.0.0.1:8428, -retentionPeriod=2y)   ← numeric series
     E:\telemetry\events.db  SQLite WAL, single writer = telemetryd                  ← events, runs, proof rows, bridge calls
     E:\telemetry\raw\       gzipped copies of every raw JSONL segment (raw is the truth; DB and VM are rebuildable)
     F:\telemetry_archive\   raw older than 90 d (HDD)
                     │
         ┌───────────┼─────────────────────────┬───────────────────────────────┐
         ▼           ▼                         ▼                               ▼
   Grafana :3000   `telemetry` CLI (WSL wrapper → python.exe;   POST alerts → pulse :8765   Lantern sparklines
   (owner)          the same pattern as rimbridge_client)        (Windows → WSL localhost)   (Windows, reads VM)
```

**Reasons, one per decision:**

1. **Two stores, because the data has two shapes.** 150 series at 1 Hz is a TSDB's job. A proof run with 105 rows, a
   deploy with a sha and file list, or a bridge call with a tool and cid is a row store's job. Forcing either into the
   other is the failure 06's single-SQLite plan would hit at T1 rates, and VictoriaMetrics alone cannot hold events.
2. **VictoriaMetrics over Prometheus:** push ingest (the game writes files, so nothing is scraped), one binary, less disk,
   PromQL-compatible. It has a native Windows build (verify the current release at install).
3. **Everything on Windows E:,** for four reasons:
   - it survives `wsl --shutdown`, which is when disk telemetry matters;
   - it stays off the ever-growing VHDX;
   - the high-rate producers already live there;
   - the disk sampler gets native `GetDiskFreeSpaceExW` without PowerShell, which ends the focus-steal that forced
     `--no-host`.
4. **Raw JSONL stays the record of truth.** VictoriaMetrics and SQLite are caches rebuildable with
   `telemetry rebuild --since`. That satisfies "commit provenance, not bulk": nothing here goes in git except code,
   dashboards and rules.
5. **One ingest daemon, never game-side push.** The game must never depend on a socket or a daemon. The existing
   file writer *is* the batched flush, and `telemetryd` is the only writer to both stores (so SQLite has one writer).
6. **RimPulse stays the one attention surface** (07 §5): alerts are POSTed to it as `red`/`amber` rows, reusing
   ack, time-to-notice and the digest. Grafana alerting stays off.
7. **WSL agents query through `python.exe`**, exactly as the bridge does. No firewall rule, no networking change. Mirrored
   networking would remove the hop (and fix bridge-from-WSL too), but it is an owner call (Q5).

**What this retires or merges:** `obs_events` (a dormant duplicate of bridge_calls: fold its useful fields, `transport`,
`timeout` and `outcome`, into `rimbridge_client._evidence` and retire it); memwatch's host path (telemetryd covers it);
05 §7a's disk-in-memwatch plan (telemetryd covers every volume). `tps_observer.py` and `health_observer.py` overlap on
"is the game alive". Keep both until telemetryd runs; then fold tps_observer's liveness checks into health_observer
(owner question 7).

---

## 6. Event correlation and regression detection

### 6.1 The events table (SQLite)

`events(id, ts, ts_end, kind, subject, seat, sha, detail JSON, src, src_ref)`. Kinds and producers:

| kind | producer | note |
|---|---|---|
| `deploy` | `deploy_custom_mods.py --apply` writes `D:\Luke\dev\_telemetry_inbox\changes.jsonl` (mods, files, sha, srchash) **and** telemetryd detects mod-folder changes itself | the detected row is the fallback, so a forgotten write still shows a change, marked `detected` |
| `build` | `winbuild.py` (mod, DLL hash, ms) | |
| `modlist` | `modset_builder.py --apply` + ModsConfig.xml hash change | |
| `game` | ledger `game` events + TPS `session`/`game`/`menu`/`save` | joined by pid and session |
| `load` | from TPS `session` to first `game` row; health `log.milestones` | load seconds as a point too |
| `bridge_hold` | ledger `bridge` take/release (span) | |
| `test_tier` | TPS `marker` arm/disarm (span) | |
| `proof_run` | `validation_core` start/end (new 2 lines) + the result JSON (span, verdict counts, mod_hash) | rows go to `proof_rows` |
| `incident`, `silence`, `flight`, `exc_first` | TPS record | |
| `oom`, `wsl_boot` | memwatch events; boot-id change | |
| `mapcomp` | persisted `jawa/map_comp_timing` | |
| `marker` | `telemetry mark "<why>"` or `jawa/telemetry_mark` | free annotations |

Every span event becomes a **Grafana annotation** on every dashboard (one annotation query per kind, toggleable).

### 6.2 Regression detection after a deploy

Passive play windows are confounded (different save, speed, map, colony size), so detection has two layers:

1. **Passive, always on:** for each `deploy` touching mod M, compare matched T2/T1 run windows before and after, matched on
   same save, same `mult`, `state=run`, same map count, and `things` within ±10 %. Compare `tickMs`, each stage's exclusive
   ms/tick, p99 from **merged histograms** (rule 4), exception rate and heap slope. Flag when the median shift
   > max(20 %, 3 × MAD) with at least 30 windows each side. Otherwise print UNMEASURED with the window counts, never "no
   change". Output: an `events` row `regression` plus a pulse amber row: *"tickMs +38 % after deploy <sha> (mods: X, Y);
   no cause is established; next: map_comp_timing"* (rule 2, no automatic blame).
2. **Perf canary (owner question 6):** a pinned benchmark save and a fixed script: load, Superfast, 3,600 ticks, test tier
   armed, per-component timing once. It runs after a deploy when the bridge is free. Same save and same procedure make
   before and after directly comparable, which passive data never is. ~3–5 min of bridge time per run.
3. **Proof-row flips:** `proof_rows` PASS → FAIL/UNMEASURED between consecutive runs of the same script; pulse amber with
   the row id and the deploys in between.
4. **Slow drifts:** a two-window CUSUM on heap/hour, log bytes/s, disk free slope ("days until full" per volume), VHDX slack.

Every detector prints its window sizes and replays a **sanity probe** (a known non-regression, and the known Rot-map
regression `f3774dd15` before vs after) so a detector that cannot see anything is caught before it reports "clean".

---

## 7. Agent interface: the `telemetry` CLI

On PATH in `~/.local/bin` like `rimflow`/`modcheck`. A WSL shell wrapper that runs `python.exe telemetry_cli.py`
(Windows side, next to the stores). Text output, compact, every block headed by **source + freshness**; absent data
prints `UNMEASURED (<why>)`, never 0.

```
telemetry health                               every source: last row, lag, rows/min, stale?, store lag
telemetry series [--grep tps]                  what exists, unit, tier, last value
telemetry query <series|MetricsQL> --since 1h [--step 1s] [--where map=0]
telemetry at "15:02" [--span 2m]               every series + events around a moment (generalises tps_record --at)
telemetry events [--kind deploy,incident] --since 24h
telemetry around deploy:<sha> [--metric tickMs] before/after windows, matched as in §6.2, with counts
telemetry runs [--mod GSS] [--last 10]         proof runs: verdict counts, wall, mod_hash
telemetry run <id> [--diff <id>]               rows, flips, plus that run's TPS/exception/bridge series
telemetry flight [--session S] [--last]        flight dumps: the spike tick, stage split, preceding ticks
telemetry exc --since 1h [--top 20]            exception signatures, counts, suppressed-by-cap, first-sight text
telemetry bridge --since 1h                    calls/min by tool, latency p50/p99, main-thread occupancy
telemetry disk                                 volumes, VHDX slack, top dirs, days-until-full
telemetry mark "<why>"                         write an annotation
telemetry tier test --ttl 60                   arm the in-game test tier through the bridge (needs the bridge hold)
telemetry rebuild --since 7d                   re-ingest raw → stores (they are caches)
```

Rule for agents (it goes in the skill): **query history before re-measuring live**. A live bridge call to read a number
that telemetry already holds is waste.

---

## 8. Owner interface

- **RimPulse / Lantern: attention.** Red/amber rows for alerts (disk < 50/20 GB, VHDX slack > 300 GB, commit > 90 %,
  OOM, tps ratio < 0.5 for 2 min unpaused, a stall, exception storm, log cap hit during a proof, proof flip, regression,
  "telemetry blind: <source>"). Plus **four sparklines** in the widget: TPS ratio, exceptions/s, host free memory, lowest
  volume free. Each row links to the Grafana panel.
- **Grafana: looking into it.** Five provisioned dashboards, as JSON files in git under `src/RimMandrake/Utils/telemetry/grafana/`:
  1. **Live test**: 1 s TPS and ratio, tickMs histogram heatmap, stage split, exceptions/s with suppressed, bridge calls and
     occupancy, heap and GC, pawns and things; annotations for markers, incidents, flight dumps.
  2. **Host and disk**: volumes, VHDX slack, memory and commit, cgroups and OOM, top directories.
  3. **Bridge**: calls/min by tool, latency, holds, proof runs.
  4. **Changes and regressions**: deploys, builds, mod-list changes against tickMs and stage costs.
  5. **Pipeline**: artpipe, selftests, ledger queue.
- He opens `http://localhost:3000` on the desktop. Remote access (phone) is not designed here.

---

## 9. Phased plan

| phase | content | effort | gate |
|---|---|---|---|
| **P0: turn on, fix, file** (≤ 1 h) | install health_observer's Windows task (owner Q7); raise `bridge_calls` rotation so it keeps more than ~10 h (or copy `.1` to E: before overwrite); file the awareness `kind` key collision; file the dormant duplicate `obs_events` | 1 h | none |
| **P1: MVP store + CLI** | `telemetryd` (Windows pythonw task): cursors over TPS, health, bridge_calls, artpipe, and over memwatch, objstore and ledger via `\\wsl.localhost`; disk sampler (C/D/E/F, VHDX, dirs hourly); deploy detection; VictoriaMetrics on E: as a task; SQLite events DB; raw gzip copies; `telemetry health/series/query/at/events/disk/mark`; `changes.jsonl` lines in deploy/winbuild/modset_builder; alerts POSTed to pulse; selftests with fake streams | **1.5–2 days** | owner Q1, Q2 |
| **P2: in-game test tier** | histogram, flight ring and dump, exception prefix counter, bridge occupancy, `jawa/telemetry_tier`, `mapcomp` rows, `tier` field; offline harness tests in `TpsMathSelfTest`; **overhead measured under the MUST 17 protocol** with the tier armed | 1.5 days + one measured run | MUST 17-style A/B; owner Q3, Q4 |
| **P3: Grafana** | install as a Windows service; two datasources; five dashboards as files; annotations; Lantern sparklines + `/api/series` | 1 day | owner Q1 |
| **P4: test runs and regression** | `validation_core` start/end events; proof rows → SQLite; `telemetry runs/run/around/flight/exc/bridge`; passive regression detector; optional perf canary; optional DuckDB for cross-run analysis | 1–1.5 days | owner Q6 |
| **P5: retire duplicates** | fold `obs_events` into `rimbridge_client`; drop memwatch's host path; fold tps_observer into health_observer; point `tps_record.md`'s "was it slow at T" to `telemetry at`; proof JSONs out of git (06 Q4) | 0.5 day | each after a week of the replacement running |

**Total ≈ 6–7 working days.** MVP (P0 + P1) ≈ 2 days and already answers: is a disk filling, is memory short, what was
TPS at T, what deployed before it got slow, how busy was the bridge. P2 answers what the owner says 1/min cannot: what
happened tick by tick during a speed-3 live test.

Model ladder (`infrastructure/agents/Agent_Policy.md`): telemetryd, the CLI and the dashboards are checkable coding
(Sonnet). The in-game P2 C# touches the tick hot path and Harmony (Opus, with a full-file review before deploy).

---

## 10. Skill outline: `skills/telemetry/` (written in P1, not before)

- **Name:** `telemetry`. **Description (trigger form):** *"Use before re-measuring anything about the game, a live test,
  the bridge, host memory, disks or the art pipeline: query recorded history first. Use when asked 'was it slow at T',
  'what changed before it got slow', 'is the disk filling', 'how busy was the bridge'; when arming the in-game test tier
  for a speed-3 live test; when an alert fires in RimPulse; when adding a collector, series, event kind or alert rule;
  and before trusting a zero from any metric."*
- **SKILL.md (lean):** the architecture diagram; the CLI verbs; the three laws (raw JSONL is truth and the stores are
  caches; stale or absent is UNMEASURED, never 0; no automatic mod blame); "history before live"; arming the test
  tier for a live test and disarming it after.
- `references/sources.md`: every source from §1 with its fields, rate, path and retention (generated from telemetryd's
  source registry, so it cannot drift).
- `references/rates.md`: the speed table (mult 1/3/6-12/15-150, measured TPS), what each tier catches, the 28 s
  log-cap arithmetic.
- `references/adding-a-series.md`: emit JSONL with `ts` from the producer; add a cursor adapter in telemetryd; never
  write a store directly; add a metrics-ledger row (id, switch, cost, decommission test) as the owner ruled.
- `references/traps.md`: the 10k Verse.Log cap and what the prefix still cannot see; the RimBridge 1,000-entry journal
  ring; NAT (WSL → Windows localhost fails); SQLite over drvfs; the awareness `kind` collision; bridge_calls' ~10 h
  retention; never average p99s; a round zero is a query bug until proven.
- Cross-links: `live-debugging-proof-harness` (proof runs feed `proof_rows`), `rimbridge`, `measuring-large-artifacts`.
- **Global promotion:** the pattern (per-producer JSONL, one ingest daemon, TSDB + row store, "stale ≠ 0") is
  project-independent. Promote it to `~/.claude/skills` only after P1 has run for two weeks.

---

## 11. Questions for the owner

Each is a real choice. **Bold** marks the recommendation.

1. **Architecture.**
   - **(a) Hybrid:** VictoriaMetrics for numbers, SQLite for events and test runs, Grafana for viewing, RimPulse for
     alerts. It handles 1 s test data and gives full dashboards. It adds three small Windows programs to keep running.
   - (b) SQLite only, with RimPulse sparklines (06's plan). Nothing new to install, but it is weak at 1 s data and has no
     real dashboards.
   - (c) VictoriaMetrics + Grafana only. Excellent graphs, but deploys and proof runs become bare 0/1 lines with no
     detail.
2. **Where it lives.**
   - **(a) E: (empty 4 TB NVMe), with raw files older than 90 days archived to F: (13 TB HDD).** It survives WSL
     restarts and stays off the WSL disk image.
   - (b) D:, next to the dev tree. Simpler paths, but it competes with artpipe and builds for the same disk.
   - (c) Inside WSL. Easiest for agents, but it goes dark during `wsl --shutdown` and grows the 975 GB disk image.
3. **In-game detail during speed-3 tests.**
   - **(a) 1-second windows plus a per-tick "flight recorder"** that saves the last ~8,000 ticks only when something goes
     wrong. It sees every spike, at small cost.
   - (b) 1-second windows only. Cheaper and simpler, but a single 500 ms tick stays a blur.
   - (c) Every tick written to disk while testing. Complete, but 17 to 3,800 rows per second, and the heaviest on the
     game.
4. **When the detailed tier runs.**
   - **(a) Armed per test by whoever holds the bridge, switching itself off after a set time.**
   - (b) Whenever the companion is in the test profile.
   - (c) Always, campaign included. This needs your 10 % campaign budget to be measured first.
5. **WSL ↔ Windows networking.**
   - **(a) Keep it as it is; agents query through `python.exe`,** as they already do for the bridge. No restart.
   - (b) Switch WSL to mirrored networking. Agents reach Windows directly, and the bridge-from-WSL limitation goes away,
     but it needs `wsl --shutdown` and changes networking for every seat.
6. **Catching slowdowns after a deploy.**
   - (a) Passive only: compare ordinary play before and after. Free, but often UNMEASURED because no two sessions match.
   - **(b) A 3–5 minute benchmark run on a fixed save after each deploy, when the bridge is free.** Directly comparable,
     at the cost of bridge time.
   - (c) The benchmark only when someone asks for it (`telemetry canary`).
7. **The Windows-side collector for game and host memory.**
   - **(a) One background program (`telemetryd`) that also runs health_observer's probes, started at logon.**
   - (b) Two programs: health_observer as built plus telemetryd.
   - (c) Install health_observer's task now (P0), and decide on merging after a week.
8. **How long to keep data.**
   - **(a) All series at full resolution for 2 years (a few GB), raw files 90 days on E:, then F:.**
   - (b) 1 year, with no raw archive.
   - (c) Forever. Under ~7 GB a year, so affordable.

---

## 12. Owner's answers after the build (2026-10-11, by card)

These replace §6.2 (per-deploy regression detection), the VHDX-slack alert in §8, and Q6/Q7 above.

1. **Deploy check (Q6)**, typed: *"Each telementry stream needs to be recorded relative to the mods that were loaded at
   the time (A) as well as their version (B). Comparing between these sets CAN be done but requires more reasoning.
   Overall thresholds of "watch out, something's wrong" alarms should generally be in place for extremely low memory or
   TPS or things like that, but otherwise it's more for same-mod lists with differing code versions being
   inter-compared with a fixed debugging savegame for reference (recommended). We should not enshrine this in
   ceremony, this is a tool that we're making available as an Operational convenience for access when needed and
   alarms to reveal problems that might not yet be realized, NOT an elaborate system to track everything ever known
   about telemetry as a function of everything else. Minimal is good, add functionality as needed by debugging."*
   Built: every game series carries `mods` (modDigest, A), `modver` (modOrderDigest: order + versions, B) and `build`;
   the per-deploy regression and proof-flip detectors are cut; `telemetry around` stays as an on-demand comparison;
   coarse alarms only (very low memory, low TPS, disk free space).
2. **Image slack**, typed: *"That's not something telemetry monitors. It should warn about huge amounts of data being
   stored (free space shrinking), NOT about "there's a lot of empty space here." That's not a danger."* The slack alert
   is removed; free-space alerts stay.
3. **Low TPS**: card pick "normal speed only", plus typed: *"we'll need to tune the thresholds to ensure bridge delay
   spikes don't constantly trigger noise. Let's watch for false positives that are noninformative and retune until
   they're gone, and reward positive detections when they also occur."* Windows where the bridge held the main thread
   over 10 % are not judged; every firing is an `alert_fired` event, graded with `telemetry label <id> tp|fp`.
4. **Game-health observer (Q7)**: card pick, off until the overhead test.
