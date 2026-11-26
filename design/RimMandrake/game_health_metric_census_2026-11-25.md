# Game health metric census, 2026-11-25 (item HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP)

Facts only, each with its source. This census does not judge any metric. It covers the 33 rows of "## Metrics ledger" in
`design/RimMandrake/game_health_record.md` (lines 155-189).

- **Read on:** host SteveDesktop (WSL, Windows user sjlewis), 2026-11-26 about 07:40Z (2026-11-25 PST). The clone is
  HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP.det.
- **What was searched:**
  - `src/`, `skills/`, `design/` and `infrastructure/`, by metric id, by symbol and by tool name. Selftests were excluded
    for READERS and counted for COUPLING. `grep` here is ugrep and ignores `--include`, so the Python-only searches were
    run with `/usr/bin/grep` over `find` lists.
  - The ledger, `infrastructure/state/ledger/events/*.jsonl`, by a JSON scanner. The scanner was sanity-checked: it found
    the known `health_observer` events.
  - The lessons.
  - The deployed companion, `D:\SteamLibrary\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`
    (5,762,048 bytes, 2026-11-25 17:41), by its strings (58,662 lines).
  - The JawaBench save-data folder,
    `C:\Users\sjlewis\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench`.
  - The Windows scheduled tasks (`schtasks /Query`, 268 tasks), the loaded systemd timers, `tasklist` and `ps`.
  - `D:\RimTest\testq\dumps`.
- **Full-list testing is retired:** owner, 2026-11-24, "Development of the mods is 100% small mod list" (standing_rulings.md:1950-1958). Any half that records only on a session with at least `full_list_min_mods` mods (200, `game_health_thresholds.json:3`) records nothing on development games from then on.
  - Counter-fact, ledger 2026-11-25T02:13Z, drop of OPS_GAME_HEALTH_DEBUG_PXQI: "session 483fab2b, 313 mods, 0 breaches ... full-list sessions still run on Archmagi". So a full-list session was still read on another host after the ruling.
- **Standing state on this host:**
  - The observer is not running. There is no `RimMandrake\Health Observer` task among the 268 tasks, and there is no `JawaBench\health` folder. No
    health_observer, belt_watchdog, ops_watch or testq worker process is in `ps`.
  - There is no `rm-metronome` or `rm-ops-watch` timer. The only loaded rm timers are ssd-check, family-clean and pool-room.
    `ops_clocks.json` `_doc` says rm-ops-watch was deleted 2026-11-23, and its phase moved into the metronome.
  - `D:\ClaudeWork\rimmandrake\game_health\` and `ops_watch\status.json` are absent.
  - There is no `health_settings.json` or `awareness_settings.json` in JawaBench, so the built-in defaults apply.
  - `companion_profile.json` holds profile `test`, which expires 2026-12-26.
  - Two RimWorldWin64.exe are running (pids 5688 and 30984). Pid 30984 writes
    `tps\tps_20261126T020325Z_b18c...30984_000.jsonl`.
  - The 40 newest TPS files hold 654 rows. 16 `context` rows carry `logErr`/`logErrLowerBound`/`privateMB`. No row
    carries hook counters or `frameHist`.
- **"Running now" means** the metric records or acts on this host now without anyone arming it.

### obs.heartbeat
1. CODE: `src/RimMandrake/Utils/health_observer.py`, which holds the source registry and `default_dir()` at :758-761 (`LocalLow/JawaBench/health`).
2. READERS:
   - program reads: `telemetry/ingest.py:346` (`val("obs.heartbeat")`; Source "health" :619-621 reads `observer_*.jsonl`); `modaudit/memory_attribution.py:368-432` (runs `health_observer.py --once --print`).
   - doc mentions: `skills/telemetry/SKILL.md:66`; `skills/telemetry/references/history.md` (124, 192, 317, 363-364, 464, 469, 541-543); `bridge_debugging_system.md:664`.
3. DEPLOYED/RUNNING: not running. There is no schtask (the install line is at health_observer.py:22-23), there is no health folder, and `telcommon.py:86` holds `"run_health_observer": False  # owner-gated`.
4. LIVE USE EVIDENCE:
   - ledger: GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN 2026-10-10, built c97c48cdc, 0.00303 cores.
   - ledger: TELEMETRY_DUPLICATES_RETIRE_AFTER_QUIET_WEEK, 2026-10-11 and 2026-10-21: "health_observer is off by owner card".
   - ledger: FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE 2026-11-02, implemented, game clauses owed.
   - The id `obs.heartbeat` itself has 0 ledger events.
5. MEASURED COST: the table says "included in the totals". The 2026-10-10 build note says 0.00303 cores for the whole observer.
6. COUPLING: delete it and the observer gaps become unreadable (table). `ingest.py:346` loses its heartbeat points. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. It has never run as a standing task on this host.

### game.identity
1. CODE: `health_observer.py` (Toolhelp snapshot source).
2. READERS:
   - program reads: `health_earlyload.py:45` (`src.get("game.identity")`); no program calls health_earlyload itself. `memory_attribution.py` reads the whole `--once` output.
   - Inside the observer, game.identity gates game.cpu, game.mainthread and game.memory. `ingest.py` does not read it.
3. DEPLOYED/RUNNING: not running (see obs.heartbeat).
4. LIVE USE EVIDENCE: 0 ledger events for the id. Only the observer's events above.
5. MEASURED COST: 7.2 ms median (table).
6. COUPLING: switch it off and game.cpu, game.mainthread and game.memory see no processes (table). health_earlyload loses its process window. Covered by `selftest_health_observer.py` and `selftest_health_spikes.py`.
7. STATUS NOW vs TABLE: "built" is true.

### game.cpu
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:329` (`rm_proc_cpu_cores`).
   - Inside the observer, `game.mainthread`'s other-threads figure reads it.
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 0.02 ms (table).
6. COUPLING: `ingest.py` loses `rm_proc_cpu_cores`, and the mainthread figure for the other threads is lost. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. The decommission cell says "no other source reads it". That is true of the sources, but `ingest.py:329` also reads it.

### game.mainthread
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:331-333` (`rm_proc_mainthread_cores`, `rm_proc_otherthreads_cores`); `modaudit/runtime.py:230` (`health_summary`, mainthread_cores_max).
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 0.01 ms steady, and 45 ms when it re-enumerates (table).
6. COUPLING: `ingest.py` and `runtime.py` `health_summary` lose the field. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. The cell "nothing reads it" is FALSE (ingest.py:331 and runtime.py:230).

### game.memory
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:334-336` (working set, private MB); `modaudit/runtime.py:223`.
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id. FULL_LIST_MEMORY_AUDIT_THIRTY_GB_PRIVATE (2026-11-02) is built on the observer stream.
5. MEASURED COST: 0.01 ms (table).
6. COUPLING: `ingest.py`, `runtime.py` and `memory_attribution.py` lose the memory fields. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. The cell "nothing reads it" is FALSE (ingest.py:334 and runtime.py:223).

### sys.memory
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:337-339` (`rm_obs_sys_*`); `modaudit/runtime.py:233` (availPhysMB_min).
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 0.13 ms (table).
6. COUPLING: `ingest.py` and `runtime.py` lose the field. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. The cell "nothing reads it" is FALSE (ingest.py:337 and runtime.py:233).

### log.growth
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:340-342` (`rm_log_bytes_per_s`, `rm_log_size_bytes`); `health_earlyload.py`, which is uncalled.
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 6.0 ms median before the binding cache, and 1.4 ms on one sample after it (table).
6. COUPLING: switch it off and log.milestones is unavailable too (table). `ingest.py` loses its log points. Covered by `selftest_health_observer.py` and `selftest_health_spikes.py`.
7. STATUS NOW vs TABLE: "built" is true.

### log.milestones
1. CODE: `health_observer.py`.
2. READERS:
   - program reads: `ingest.py:343-345` (event `log_milestone`).
3. DEPLOYED/RUNNING: not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 0.01 ms steady, and 23 ms per new-log scan (table).
6. COUPLING: `ingest.py` loses its `log_milestone` events. Covered by `selftest_health_observer.py`.
7. STATUS NOW vs TABLE: "built" is true. The cell "nothing reads it" is FALSE (ingest.py:343).

### watchdog.cpu-trend
1. CODE: `src/RimMandrake/Utils/belt_watchdog.py:409`, `def cpu_rate(game, now, state_dir=None, mono=None)`. It is called at :480 as `rate, nr_for = cpu_rate(game, now, hb_dir)`.
2. READERS:
   - program reads: the cpu_rate call in `belt_watchdog.py` itself (the WEDGED "Not Responding for X" verdict uses nr_for). No program launches belt_watchdog.
   - doc mentions: `skills/live-debugging-proof-harness/SKILL.md:516` and `references/run-checklists.md:87` (run by hand or by Monitor). `load_policy.READERS` lists belt_watchdog.
3. DEPLOYED/RUNNING: not running. It runs only by hand, and no belt_watchdog process exists.
4. LIVE USE EVIDENCE: 1 ledger event for `cpu_rate`, TPS_HOOKS_HARDEN 2026-10-10 (a wording fix). 0 events for the id `cpu-trend`.
5. MEASURED COST: UNMEASURED (table). It is also absent from the 2026-10-15 note.
6. COUPLING: delete the call at :480 and the WEDGED verdict loses its Not-Responding timer (nr_for). Covered by `selftest_belt_watchdog.py`.
7. STATUS NOW vs TABLE: "built (fixed)" is true.

### forensics.load-tree
1. CODE: `src/RimMandrake/Utils/health_forensics.py` subcommand `load-tree` (add_parser at :306).
2. READERS:
   - program reads: no reader found. The searches were `health_forensics` across all `.py` (only the file itself), `load_tree` and `load-tree`.
   - doc mentions: `game_health_record.md` and `bridge_debugging_system.md`.
3. DEPLOYED/RUNNING: on demand only. Not running.
4. LIVE USE EVIDENCE: ledger LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED (file, note and reconcile 2026-10-10/11): "UNMEASURED vs real output: no DeepProfiler tree in 18 archived logs". No use after that.
5. MEASURED COST: UNMEASURED on real data (table).
6. COUPLING: nothing breaks except `selftest_health_forensics.py`.
7. STATUS NOW vs TABLE: "built" is true.

### forensics.save-census
1. CODE: `health_forensics.py` subcommand `save-census` (:310).
2. READERS:
   - program reads: no reader found (same searches, plus `save_census`).
   - doc mentions: `game_health_record.md` and `bridge_debugging_system.md`.
3. DEPLOYED/RUNNING: on demand only. Not running.
4. LIVE USE EVIDENCE: 1 ledger event, the build note of 2026-10-10 (16.7 MB in 0.5 s; 49.5 MB in 1.4 s, 18 MB RSS). No use after that.
5. MEASURED COST: 0.5 s for 16.7 MB, and 1.4 s with 18 MB RSS for 49.5 MB (table, which matches the ledger).
6. COUPLING: nothing breaks except `selftest_health_forensics.py`.
7. STATUS NOW vs TABLE: "built" is true.

### forensics.content-identity
1. CODE: `health_forensics.py:265` `def content_identity(save=None, mods_config=None, mod_roots=(), settings_dir=None)`, subcommand at :314 and :320.
2. READERS:
   - program reads: no reader found (searches: `content_identity`, `content-identity`, `health_forensics`).
   - doc mentions: `game_health_record.md`.
3. DEPLOYED/RUNNING: on demand only. Not running.
4. LIVE USE EVIDENCE: 0 ledger events for the id. The 2026-10-10 note says "Owed: content identity".
5. MEASURED COST: UNMEASURED on the real list (table).
6. COUPLING: nothing breaks except `selftest_health_forensics.py`.
7. STATUS NOW vs TABLE: "built" is true. The cell says "the real 600-mod list", but the owner's list is 317-321 mods (`game_health_thresholds.json` doc).

### tps.frame-hist
1. CODE: `bridgetools/JawaBench.BridgeTools/JawaBenchHealth.cs` (`RootPrefix` :211, patched at :198 on Root.Update) and `JawaBenchHealthCore.cs`. The string is in the deployed DLL. `JawaBenchTpsSampler.cs:437` has a separate `RootPrefix` of its own.
2. READERS:
   - program reads: `modcheck/live_queue/bridge_bundle_proof.py:1058` (`L.call("jawa/health", action="arm", minutes=5)`) and :1061 (status frameHist, FRAME clause).
   - doc mentions: lesson `infrastructure/state/lessons/20261112T182658Z-BENCH-jawa-health-tps-frame-hist-frame.md`; handoffs BENCH_REBOOT_HANDOFF_202611122135.md and _202611240601.md; `pipeline_sleepers_census_2026-11-15.tsv`.
3. DEPLOYED/RUNNING: deployed (DLL 2026-11-25). Not running: it records only while jawa/health is armed (TTL), and no `frameHist` is in the newest TPS rows.
4. LIVE USE EVIDENCE:
   - HEALTH_METRICS 2026-10-15 cost note.
   - RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG (CONDUCTOR 2026-11-12).
   - RIMMANDRAKE_PROVE_KNOCKBACK_ALL_FLY_PERF (OWNER 2026-11-12), measured with frame-hist on the 13-mod list: a SpinWait of 1,095 ms read as 1094.963.
5. MEASURED COST: the table says UNMEASURED. The 2026-10-15 BENCH r3 note says 33,566 calls, 0.93 us mean, 31.1 ms total.
6. COUPLING: the bridge_bundle_proof FRAME clause breaks. spike.gc-timing shares the JawaBenchHealth `RootPrefix` (table). Covered by `HealthSelfTest/Program.cs` through `selftest_health_core.py`.
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE (in the deployed DLL, and used live 2026-11-12). "UNMEASURED" is FALSE (2026-10-15 note).

### tps.log-counts
1. CODE: `JawaBenchHealth.cs` (`OnLog`/`ReadCap` per the table) and `JawaBenchHealthCore.cs`. The string is in the deployed DLL.
2. READERS:
   - program reads: `bridgetools/deepfire_log_check.py:43` (status `log.state`, `capResets` at :108); `prove_biome_quicktest.py:35`, `prove_biome_timelapse.py:40`, `prove_contagion_burn.py:21` and `prove_forge_cycle_ticks.py:27` (status "log").
3. DEPLOYED/RUNNING: deployed. Not running: it records only while armed.
4. LIVE USE EVIDENCE: only the 2026-10-15 cost note in the ledger. 0 other events for the id.
5. MEASURED COST: the table says UNMEASURED. The 2026-10-15 note says 0.04 ms.
6. COUPLING: `deepfire_log_check.py` and the four prove_* scripts lose the log state. The observer's `log.cap-reached` stays (table). Covered by `HealthSelfTest/Program.cs` (the `logCounts` symbol was not found by name; the header comment at :2 names it) and `bridgetools/selftest_deepfire_log_check.py`.
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE (in the deployed DLL). "UNMEASURED" is FALSE.

### tps.bridge-occupancy
1. CODE: `JawaBenchHealth.InstallHooks` (two RimBridgeServer pump patches per the table) and `JawaBenchHealthCore.cs`. The string is in the deployed DLL.
2. READERS:
   - program reads: no reader found. `/usr/bin/grep` across all non-selftest `.py` files for `bridgeOccupancy`, `bridge-occupancy` and `"occupancy"` returned 0 hits.
   - The `"bridgeOccupancy":true` in TPS `session` rows is the TPS recorder's own settings flag (`JawaBenchTpsTierTools.cs:21`), not this metric.
3. DEPLOYED/RUNNING: deployed. Not running: it records only while armed.
4. LIVE USE EVIDENCE: only the 2026-10-15 cost note.
5. MEASURED COST: the table says UNMEASURED. The 2026-10-15 note says 100,700 calls, 2.0 us, 202 ms, the largest share of the ~0.26 s total.
6. COUPLING: no program breaks. Covered by `HealthSelfTest/Program.cs:125`.
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE. "UNMEASURED" is FALSE.

### tps.capability-inventory
1. CODE: `JawaBenchHealthCapabilities` (in the deployed DLL).
2. READERS:
   - program reads: no reader found (searches: `capabilities`, `capability-inventory`, `probe_end` in non-selftest `.py`; the only hits are rimflow's unrelated `capabilities`).
3. DEPLOYED/RUNNING: deployed. On demand (`jawa/health` status or `action=probe`). Not running.
4. LIVE USE EVIDENCE: 0 ledger events.
5. MEASURED COST: UNMEASURED (table). It is not in the 2026-10-15 note.
6. COUPLING: no program breaks. Covered by `HealthSelfTest/Program.cs` and `selftest_health_core.py`.
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE (`JawaBenchHealthCapabilities` is in the deployed DLL).

### opt.own-counters
1. CODE: `OwnPreset` in `JawaBenchHealthProfiler.cs` (in the deployed DLL). `jawa/health_profile action=start preset=own`.
2. READERS:
   - program reads: `bridgetools/own_preset_check.py`; `Pyrelands/validation.py:2189-2228` and 2345-2348.
   - doc mentions: `live_proofs/OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN.criteria`.
3. DEPLOYED/RUNNING: deployed. On demand and expiring. Not running.
4. LIVE USE EVIDENCE: OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN (filed 2026-10-15, implemented 2026-11-03 and 2026-11-05); OWN_PRESET_PRUNE_FURNACEHERD_GHOST_KEY 2026-11-05.
5. MEASURED COST: UNMEASURED (table). It is shared with opt.profiler, which the 2026-10-15 note gives as 0.
6. COUPLING: `own_preset_check.py` and the Pyrelands validation profile steps break. Covered by `HealthSelfTest/Program.cs` (`OwnPreset`).
7. STATUS NOW vs TABLE: "merged into opt.profiler" is true.

### opt.profiler
1. CODE: `JawaBenchHealthProfiler.cs` and the tool `jawa/health_profile` (both in the deployed DLL).
2. READERS:
   - program reads: `Pyrelands/validation.py:2189-2228`, 2345-2348; `perf/mappretick_window.py:263-264`; `perf/sheetrain_deluge_window.py`; `perf/spore_emitter_window.py`; `bridgetools/own_preset_check.py`; `northstar_driver/tool_schemas.json`.
   - doc mentions: `skills/live-debugging-proof-harness/references/perf.md`.
3. DEPLOYED/RUNNING: deployed. On demand (10 min by default, 60 at most). Not running.
4. LIVE USE EVIDENCE: 21 ledger events. The decision uses:
   - HOSE_FRAME_FIX_CHOKES_325_BASIN_MAP 2026-10-26 (RefreshMates max 82.7 s);
   - HOSE_LAY_FIX_SYNC_RELAY_IN_DRAW and HOSE_LAY_FIX_GC_STORM_FROM_WORKER 2026-10-26;
   - GSS_SNAPSHOT_MEASURE_REBUILD_PER_DIG 2026-10-26 (CordBuilder.Build 15.29 ms mean);
   - RIMMANDRAKE_TRACE_PYRE_ASHFALL_FIRE_IN_FIRST_LIGHTNING_WINDOW 2026-11-21;
   - RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP 2026-11-21 ("measured nothing");
   - RIMMANDRAKE_TELL_HIM_ROT_SPORE_MUSHROOM_PERFORMANCE_VERDICT_HIS_HUNCH 2026-11-23.
5. MEASURED COST: the table says UNMEASURED. The 2026-10-15 note says 0 when not started.
6. COUPLING: Pyrelands validation, the three perf windows and own_preset_check break. Covered by `HealthSelfTest/Program.cs`, `selftest_health_core.py` and `Pyrelands/selftest_pyrelands_site.py`.
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE (deployed, and used live in at least 7 items 2026-10-26..11-23). "UNMEASURED" is FALSE as an idle cost (2026-10-15 note).

### spike.gc-timing
1. CODE: the GC half of `JawaBenchHealth.cs` `RootPrefix`; `JawaBenchHealthCore.cs:38` (`MGc = "spike.gc-timing"`) and :435-464 (`gcCountChangedDuringGap`). The string is in the deployed DLL.
2. READERS:
   - program reads: no reader found (searches: `gcCountChanged`, `gc-timing`, `gapGc`, `"gc"` in non-selftest `.py`). The hits `heap_ratchet.py:77` and `ingest.py:104` are the TPS sample's `gc` count, not this metric.
3. DEPLOYED/RUNNING: deployed. Not running: it records only while armed.
4. LIVE USE EVIDENCE: only the 2026-10-15 cost note.
5. MEASURED COST: the table says UNMEASURED. The 2026-10-15 note says 26.2 ms.
6. COUPLING: no program breaks. It shares `RootPrefix` with frame-hist. Covered by `HealthSelfTest/Program.cs` (`gcPause`).
7. STATUS NOW vs TABLE: "written, not deployed" is FALSE. "UNMEASURED" is FALSE.

### spike.early-load
1. CODE: `src/RimMandrake/Utils/health_earlyload.py`, which imports health_observer as HO at :136.
2. READERS:
   - program reads: no reader found. `health_earlyload` appears in no other non-selftest `.py`.
3. DEPLOYED/RUNNING: not running. It needs the observer stream, which does not exist on this host.
4. LIVE USE EVIDENCE: only the 2026-10-15 note in the ledger. GC_EARLYLOAD_DUMPS_PROBE_SHOW_VALUE_FIRST was filed 2026-10-10.
5. MEASURED COST: UNMEASURED (table). It has no probe of its own.
6. COUPLING: nothing breaks except `selftest_health_spikes.py`.
7. STATUS NOW vs TABLE: "written, not deployed" is true in effect: it is an offline reader with no input stream.

### spike.minidump
1. CODE: `src/RimMandrake/Utils/health_minidump.py` (`AUTOMATIC = False` :54, `BEFORE_KILL_AUTOMATIC = True` :55); `health_minidump_spike.py`; `minidump_read.py`.
2. READERS:
   - program reads: `infrastructure/stevedesktop/worker.py:1820` `dump_game`, called at :1228 ("wedged") and :1732 ("hang%d"). It runs `health_minidump.py --before-kill --incident ... --dir TESTQ_HOME/dumps`, and only on STEVE_LANE. `minidump_read.py` reads dumps, by hand.
3. DEPLOYED/RUNNING:
   - It fired live 6 times: `D:\RimTest\testq\dumps` holds 6 `.dmp` files with `.dmp.json` sidecars and 6 `*_wedged.claim` files, dated 2026-11-11, 11-13, 11-14, 11-15 and 11-21.
   - Example: `rimworld_17588_20261121T045051Z.dmp`, 6,051,960 bytes, "mode":"snapshot", "suspendedMs":173.7, "status":"ok".
   - No worker.py process is running now.
4. LIVE USE EVIDENCE: MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL, implemented 2026-11-06, was DROPPED by the OWNER 2026-11-24: "diagnosing game stops ends ... health_minidump.py stays with AUTOMATIC=False". HEALTH_MINIDUMP_FIX_FOREIGN_DUMP_PRUNE 2026-10-26. 0 events for `dump_game`/`before-kill`.
5. MEASURED COST: the table gives a stand-in, snapshot mode: a pause of 4-58 ms, ~105 KB. The live sidecar of 2026-11-21 shows a 173.7 ms suspend, 1139 ms duration and ~6 MB per dump on a 4.0 GB working set.
6. COUPLING: delete it and `worker.py` `dump_game` (:1228, :1732) breaks. Covered by `selftest_health_spikes.py`.
7. STATUS NOW vs TABLE: "live dump of the game owed" is FALSE. 6 live before-kill dumps exist (2026-11-11..11-21), and the owner dropped the item 2026-11-24. The stand-in cost understates the live suspend (173.7 ms vs 4-58 ms).

### aware.incident-journal
1. CODE: `JawaBenchAwareness.cs`, `JawaBenchAwarenessCore.cs` and `JawaBenchAwarenessTools.cs` (`jawa/awareness`). The string is in the deployed DLL.
2. READERS:
   - program reads: `bridge_bundle_proof.py:943-1419` (AWARE); `modcheck/live_queue/map_awareness_proof.py:417,685` (arm 30 min); `tps_record.py:1173` (renders `awareness` rows).
3. DEPLOYED/RUNNING: deployed, under the test profile. Not running: it records only while armed (TTL), and no awareness rows are in the 40 newest TPS files.
4. LIVE USE EVIDENCE:
   - PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN verify 2026-10-10.
   - MAP_AWARENESS_PROVE_ON_A_QUIET_MAP implemented 2026-11-03.
   - VISITOR_DETECTORS_MEND_NAME_THE_STRANGER verify 2026-11-25 (map_awareness_proof A4).
5. MEASURED COST: MEASURED 2026-10-10 live: 3 calls, mean 2836 us, max 7980 us (table).
6. COUPLING: the bridge_bundle_proof AWARE clause and map_awareness_proof break. Covered by `AwarenessSelfTest/Program.cs` through `selftest_map_awareness_core.py`, and `modcheck/selftest_awareness.py`.
7. STATUS NOW vs TABLE: "deployed (test profile)" is true.

### aware.origin-context
1. CODE: `JawaBenchAwareness*.cs`. The string `origin-context` is in the deployed DLL.
2. READERS:
   - program reads: through `jawa/pawn_origin` in `bridge_bundle_proof.py:1427`, `map_awareness_proof.py:420` and `modcheck/quiet_site.py:368`.
3. DEPLOYED/RUNNING: deployed, under the test profile. It records only while armed.
4. LIVE USE EVIDENCE: 0 ledger events for the id. For `pawn_origin`: TESTENV_FOGGED_MECH_HARDEN_WOKE_ON_REVEAL 2026-10-15, "pawn_origin notFound after the save/load epoch".
5. MEASURED COST: 0 calls in the 2026-10-10 session, unexercised (table).
6. COUPLING: the generation and spawn rows lose their chain (table), and `quiet_site.py:368` reads pawn_origin. Covered by `AwarenessSelfTest/Program.cs`.
7. STATUS NOW vs TABLE: true.

### aware.origin-generation
1. CODE: `JawaBenchAwareness*.cs`. The GeneratePawn hook is installed lazily. The string is in the deployed DLL.
2. READERS:
   - program reads: through `jawa/pawn_origin` (the same three callers).
3. DEPLOYED/RUNNING: deployed, under the test profile. It records only while armed.
4. LIVE USE EVIDENCE:
   - PAWN_ORIGIN_BUILD_SAY_ORIGIN_UNKNOWN verify 2026-10-10.
   - AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE notes, CONDUCTOR 2026-11-25. Their next steps say "TPS, PROFILE, HOOKS owed", and `thing_explain` destroyed-pawn fix 04ff1e5aac is "not deployed".
5. MEASURED COST: 7 calls, mean 885 us, max 4071 us (table).
6. COUPLING: pawn_origin loses its generation half. Covered by `AwarenessSelfTest/Program.cs`.
7. STATUS NOW vs TABLE: true.

### aware.origin-spawn
1. CODE: `JawaBenchAwareness*.cs`. The string is in the deployed DLL.
2. READERS:
   - program reads: through `jawa/pawn_origin` (the same three callers).
3. DEPLOYED/RUNNING: deployed, under the test profile. It records only while armed.
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 28 calls, mean 287 us, max 5624 us (table).
6. COUPLING: pawn_origin loses its spawn half (table). Covered by `AwarenessSelfTest/Program.cs`.
7. STATUS NOW vs TABLE: true.

### aware.disk-rows
1. CODE: `JawaBenchAwareness*.cs` (TPS rows of kind `awareness`). The string is in the deployed DLL.
2. READERS:
   - program reads: `tps_record.py:455` (kind list) and :1173-1174 (renders `AWARE` lines).
3. DEPLOYED/RUNNING: deployed, under the test profile. Not running now: there are 0 `awareness` rows in the 40 newest TPS files (654 rows).
4. LIVE USE EVIDENCE: 0 ledger events for the id.
5. MEASURED COST: 0 calls in the 2026-10-10 session, unexercised (table).
6. COUPLING: `tps_record.py` loses its AWARE lines. Covered by `AwarenessSelfTest/Program.cs` ("disk" ×5) and `selftest_tps_record.py`.
7. STATUS NOW vs TABLE: true.

### aware.wild-spawner-block
1. CODE: `JawaBenchAwareness*.cs` (`jawa/wild_spawner_block`). It is in the deployed DLL.
2. READERS:
   - program reads: `modcheck/helpers.py:345-352` (the quiet-world helper, with restore); `FlowWorks/northstar/big_pit_scene.py:473`; `HugeThings/northstar/passage_pool_driver.py:160`; `walls_slots_live.py:1039` and 2506; `bridge_bundle_proof.py:1031`.
3. DEPLOYED/RUNNING: deployed, under the test profile. On demand, with a TTL.
4. LIVE USE EVIDENCE: THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER and BRIDGE_TARGETS_HARDEN_STALE_AFTER_RELOAD, both implemented 2026-10-10; MAP_AWARENESS_PROVE_ON_A_QUIET_MAP note 2026-10-10.
5. MEASURED COST: UNMEASURED (table).
6. COUPLING: the quiet-world helper and four scene drivers break. Covered by `AwarenessSelfTest/Program.cs` (by suite; the symbol was not found by name).
7. STATUS NOW vs TABLE: "built, not deployed" is FALSE (in the deployed DLL, and called by 5 programs).

### companion.profile-gate
1. CODE: `JawaBenchCompanionSafety.cs` and `JawaBenchSafetyCore.cs` (both in the deployed DLL).
2. READERS:
   - program reads: every jawa tool call passes the gate. `rimflow/companion_grant.py:2,57` reads and writes `companion_profile.json`. FlowWorks validation 2026-10-11 JSONs record "REFUSED in the CAMPAIGN profile".
3. DEPLOYED/RUNNING: RUNNING. It is in the deployed DLL, `companion_profile.json` holds profile `test` until 2026-12-26, and two games are running.
4. LIVE USE EVIDENCE:
   - COMPANION_PROFILE_ENFORCE_SAFE_BY_DEFAULT filed 2026-10-10.
   - COMPANION_GRANT_WIRE_LAPSES_AT_BEDTIME 2026-10-29: a lapse bounced 5 items.
   - GRANT_RESTORE_CAMPAIGN_WHEN_HE_PLAYS, OWNER 2026-11-07.
5. MEASURED COST: UNMEASURED (table).
6. COUPLING: every test-only jawa tool and `companion_grant.py` depend on it. Covered by `AwarenessSelfTest` (it compiles `JawaBenchSafetyCore.cs` and `UnitsSafety.cs`) through `selftest_map_awareness_core.py`, and by `prove_companion_safety_fixes.py`.
7. STATUS NOW vs TABLE: "built, not deployed" is FALSE (deployed and gating now).

### companion.hook-coverage
1. CODE: `JawaBenchHookGuard.cs` and `JawaBenchTpsSampler.cs`; `foreignThread` occurs 12 times in the DLL strings. It is reported in `jawa/tps_report` `hooks`.
2. READERS:
   - program reads: `bridge_bundle_proof.py:205-214` (`v_HOOKS`) and :924-939 (`g_HOOKS`, families `hooks`/`attributionHooks`, `foreignThreadRejects`). `belt_watchdog.py:330` and `venomvine_islands_live.py:253` call jawa/tps_report.
3. DEPLOYED/RUNNING: RUNNING. The counters count in the running companion whenever the TPS recorder hooks are installed. They are written to no file: 0 hook-counter strings appear in the newest TPS rows.
4. LIVE USE EVIDENCE: 0 ledger events for the id. AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE 2026-11-25 lists the bundle's HOOKS clause as owed.
5. MEASURED COST: UNMEASURED live; counters only (table).
6. COUPLING: the bridge_bundle_proof HOOKS clause breaks. Covered by `selftest_tps_record.py` and `selftest_bridge_hooks.py` (`hooks`). The symbol `HookCoverage` was not found in any selftest.
7. STATUS NOW vs TABLE: "built, not deployed" is FALSE (`JawaBenchHookGuard` is in the deployed DLL).

### aware.thing-explain
1. CODE: `jawa/thing_explain` (in the deployed DLL); `JawaBenchAwarenessTools.cs`.
2. READERS:
   - program reads: `GelatinousSlime/live_kit_art.py:151`; `Miasma/tests/warden_mother_live_proof.py:95,104`; `bridge_bundle_proof.py:905-920`; `map_awareness_proof.py:556-557`.
3. DEPLOYED/RUNNING: deployed. On demand. The vanished-id fix 04ff1e5aac / db9b97d9c4 is "not deployed" (ledger 2026-11-25).
4. LIVE USE EVIDENCE: 8 events. THING_LOOKUP_BUILD_OWNER_IS_NOT_PAINTER 2026-10-10; MAP_AWARENESS_PROVE_ON_A_QUIET_MAP and TAOZIN_SPLIT_BUILD_ONE_WORM_BECOMES_TWO 2026-11-03/05; AWARENESS_GENPAWN_TAME_ARM_BEFORE_USE 2026-11-25.
5. MEASURED COST: on demand; per-call cost metered (table).
6. COUPLING: 4 programs break, against the table's "nothing else reads it". Covered by `AwarenessSelfTest/Program.cs` (`thing_explain`).
7. STATUS NOW vs TABLE: "built, not deployed" is FALSE (in the deployed DLL). The decommission cell "nothing else reads it" is FALSE (4 programs).

### scene.report
1. CODE: `src/RimMandrake/Utils/modcheck/scene_report.py`.
2. READERS:
   - program reads: `modcheck/watch.py:122` (Watch writes one at baseline); `modcheck/live_queue/map_awareness_proof.py:491`.
3. DEPLOYED/RUNNING: Python, on demand. Not running.
4. LIVE USE EVIDENCE: VISITOR_DETECTORS_MEND_NAME_THE_STRANGER file and implemented 2026-10-10, and verify 2026-11-25 ×2: "map_awareness_proof A4 names manhunter Warg41996 and player joiner Human41997 through scene_report".
5. MEASURED COST: ~10 bridge reads per report (table).
6. COUPLING: `watch.py` (scene=True) and map_awareness_proof A4 break. Covered by `modcheck/selftest_awareness.py`.
7. STATUS NOW vs TABLE: "built" is true.

### health.session-check
1. CODE:
   - offline: `src/RimMandrake/Utils/game_health_check.py` (history `$RM_GAME_HEALTH_DIR`, default `D:\ClaudeWork\rimmandrake\game_health\history.jsonl`, :82-86; full-list filter :620) and `game_health_thresholds.json`.
   - companion: `JawaBenchSessionHealth.cs`, called from `JawaBenchTpsSampler.cs:754` (`sb.Append(JawaBenchSessionHealth.Fields())`) and `JawaBenchTextureMemoryTools.cs:243`. It is in the deployed DLL.
2. READERS:
   - program reads: `ops_watch.py:2545-2584` (c_tps runs `record --json` and `latest --json`, giving keys tps.health_breaches, tps.health_age_h and tps.health_sessions; listed at :4886); `acceptance_game_health_growth_per_game.py:21`.
   - doc mentions: `log_rise_census.py:7`.
3. DEPLOYED/RUNNING:
   - The companion half is RUNNING: 16 `context` rows in the newest TPS files, up to 2026-11-26, carry `logErr`, `logErrLowerBound` and `privateMB`.
   - The offline half is not running on this host: there is no history folder and no ops_watch timer.
   - On another host the ledger shows ops_watch raising and clearing on tps.health_breaches 2026-11-23 and 2026-11-24.
   - It records only sessions of 200 or more mods. Full-list testing has been retired since 2026-11-24.
4. LIVE USE EVIDENCE: 23 ledger events for `game_health_check`.
   - OPS_GAME_HEALTH_DEBUG_PXQI: 2026-11-15, managed growth 1036.6 vs 1024; 2026-11-23, a 434-min session, stall_max_s 38.55 vs limit 30; 2026-11-25, dropped, "session 483fab2b, 313 mods, 0 breaches ... full-list sessions still run on Archmagi".
   - LOG_BOUND_DECIDE_COLD_LOAD_ALWAYS_GUILTY 2026-11-10.
   - RIMMASTER_WIRE_STEVEDESKTOP_TELEMETRY_FLYING_BLIND 2026-11-24.
   - 0 events for the id `session-check`.
5. MEASURED COST: offline, about 3 s over the whole TPS record. In game: UNMEASURED (table).
6. COUPLING: ops_watch's tps family (3 keys) and the acceptance test break. The companion fields also feed the texture-memory tool output (:243). Covered by `selftest_game_health_check.py`.
7. STATUS NOW vs TABLE: "companion fields written, not deployed" is FALSE (in the deployed DLL and writing context rows now).

### tps.presentation-fps
1. CODE: not built. The id occurs only in `JawaBenchHealthProfiler.cs` (as a mention) and in the record.
2. READERS:
   - program reads: no reader found (search: `presentation-fps` and `presentation`).
3. DEPLOYED/RUNNING: not built.
4. LIVE USE EVIDENCE: 0 ledger events.
5. MEASURED COST: UNMEASURED (table).
6. COUPLING: none.
7. STATUS NOW vs TABLE: "unsupported (for now)" is true.

## False cells in the ledger

1. **Status "written, not deployed" for 6 rows:**
   - The rows are `tps.frame-hist`, `tps.log-counts`, `tps.bridge-occupancy`, `tps.capability-inventory`, `opt.profiler` and `spike.gc-timing`.
   - Their code is in the deployed DLL of 2026-11-25. The DLL strings include the metric ids, `JawaBenchHealthCapabilities`, `JawaBenchHealthProfiler`, `jawa/health` and `jawa/health_profile`.
   - Live use: frame-hist 2026-11-12, profiler in 7 or more items 2026-10-26..11-23.
2. **Measured cost "UNMEASURED" for 5 rows:** `tps.frame-hist`, `tps.log-counts`, `tps.bridge-occupancy`, `spike.gc-timing` and `opt.profiler`. The 2026-10-15 BENCH r3 note measured them: 31.1 ms, 0.04 ms, 202 ms, 26.2 ms and 0. The total was ~0.26 s over ~500 s.
3. **Status "built, not deployed" for 4 rows:**
   - The rows are `aware.wild-spawner-block`, `companion.profile-gate`, `companion.hook-coverage` and `aware.thing-explain`.
   - They are all in the deployed DLL.
   - `companion_profile.json` (profile `test`) is live.
   - The tools are called by 5, all, 1 and 4 programs respectively.
4. **`health.session-check`, "companion fields written, not deployed":** `JawaBenchSessionHealth` is in the DLL, and context rows dated 2026-11-26 carry `logErr`/`logErrLowerBound`/`privateMB`.
5. **`spike.minidump`, "live dump of the game owed":**
   - 6 live before-kill dumps are in `D:\RimTest\testq\dumps` (2026-11-11..11-21), written by `worker.py` `dump_game`.
   - The owner dropped MINIDUMP_PROVE_SPIKE_BEFORE_THE_KILL 2026-11-24.
   - The stand-in cost (pause 4-58 ms) is below the live suspend of 173.7 ms.
6. **Decommission "nothing reads it" for 4 rows:**
   - `game.mainthread`: `ingest.py:331`, `runtime.py:230`.
   - `game.memory`: `ingest.py:334`, `runtime.py:223`.
   - `sys.memory`: `ingest.py:337`, `runtime.py:233`.
   - `log.milestones`: `ingest.py:343`.
7. **`aware.thing-explain`, decommission "nothing else reads it":** 4 programs call it (live_kit_art.py, warden_mother_live_proof.py, bridge_bundle_proof.py, map_awareness_proof.py).
8. **`forensics.content-identity`, "the real 600-mod list":** the owner's list is 317-321 mods (`game_health_thresholds.json` doc), and the 2026-11-25 session read had 313.

Count: 8 groups, 24 cells.

**Outside the table, same file:**
- **Lines 104-105:** "ops_watch's `tps` family runs `game_health_check.py record` on every pass (`rm-ops-watch.timer`)". That unit was deleted 2026-11-23 (`ops_clocks.json` `_doc`; `operations.md:68-74`), and its phase moved into rm-metronome.
- **Lines 135-136, Contracts table:** `tps.frame-hist` and `tps.log-counts` are described as written but not deployed. That is false for the same DLL evidence as item 1.
- **Line 137, Contracts "Harmony safety | owed (TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS) | FAIL until fixed":** the item has been "implemented" since 2026-10-10 (FOUNDRY) and was re-homed to BENCH 2026-11-03, with no verify event. "Owed" is out of date. Whether the work passes is UNKNOWN: there is no verify event.
- **Lines 205-207, "Not installed as a standing task yet":** this is still TRUE on this host.
