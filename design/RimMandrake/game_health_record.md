# The game-health record: metrics beyond TPS

The owner ruled **"Everything at once"** by question card on 2026-10-10. The design is option F from the combined
Opus design and GPT review: evidence first, in small steps, with nothing heavier going always-on until the TPS
full-list overhead test passes (`BRIDGE_TPS_REVIEW2_FIXES_1` MUST 17). The owner also ruled that **every metric must be
evaluable and removable later**. He will judge each one's worth and cost after the fact and switch off whatever does not
earn its keep. So every source has a stable id, its own switch, and a measured cost written into the record. The
metrics ledger below is where that judgement happens (`HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP`).

The TPS record itself is `design/RimMandrake/tps_record.md`.

## Rules that bind every source

These come from the GPT review. A change that breaks one of them is a defect.

1. **Unavailable is never zero.** Each source reports `ok` (with a value), `unavailable` (with a reason), `failed`
   (with the error) or `off`. A reader prints the word, never `0`.
2. **No automatic mod blame.** Cost and attribution are separate questions. The readers print observations side by
   side and end with "no cause is established".
3. **Process-scoped counters are not reset at a game change.** Process CPU, log suppression and process memory
   accumulate across reloads, and that accumulation is what reload investigations look for.
4. **Merge histograms; never average p99s.** Keep the bucket definitions and their version with the data.
5. **Bulk artifacts go in separate capped files**, never in giant JSONL rows. The main stream holds only a reference.
6. **Label a coincidence as a coincidence.** For example `gcCountChangedDuringGap`, never `gcPauseMs`. A process at
   one core is a process total, not "the main thread spinning".
7. **The Verse.Log cap is 10,000 messages.** This comes from `StopLoggingAtMessageCount = 10000` in decompiled 1.6
   `Verse/Log.cs` (RimSage, 2026-10-10). Every Unity message counts toward it, via
   `Notify_MessageReceivedThreadedInternal`. At the cap the engine sets `Debug.unityLogger.logEnabled = false`. Only
   `Log.Clear` calls `ResetMessageCount`, which is what the debug log window's Clear button does. After the cap, the
   reader must say **"emission suppressed; error activity unknown"**. (`belt_watchdog.py` and a 2026-10-04 lesson both
   said 1,000. Both are corrected.)

## What is built

### 1. External observer: `src/RimMandrake/Utils/health_observer.py` (`GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN`)

This is one long-lived Windows process (`python.exe` or `pythonw.exe`, stdlib and ctypes only) that injects no game
code. A lock file allows only one instance to run, so a scheduled task can safely re-start it every few minutes.

- **Stream** (outside git): `<LocalLow>\JawaBench\health\observer_<startUtc>_<collectorPid>_<seg>.jsonl`.
  - Segments are 4 MB.
  - Retention is 14 days with a 256 MB cap, and the live segment is never pruned.
  - Every row carries `v` (schema), `seq` (strictly increasing across segments), `collector.id` (host, pid and
    start time) and `utc`. Samples also carry `mono`.
  - Row kinds are `start` (switches, unknown settings, the question each source answers), `sample`, `event` and
    `stop` (totals).
  - `collector_last.json` is rewritten after every sample.
- **Cadence**: every 5 s while a RimWorld process exists and every 30 s otherwise. Collection is deadline based, and
  after a machine sleep the schedule re-anchors.
- **Switches**: `health_observer_settings.json` takes `{"sources": {"<id>": false}}`, or pass `--off <id>` on the
  command line. An unknown id is reported on the `start` row. `obs.heartbeat` cannot be switched off.
- **Game identity** is pid plus creation time. The observer **holds** a process handle for each game it watches. That
  stops Windows from recycling the pid while it watches, and gives it the real exit code (`game-exit`).
- **Main thread**: the observer takes the earliest-created thread of the process to be the main thread. It holds a
  handle to that thread and reads it with `GetThreadTimes`. This is labelled **assumed** on every row, because it is
  not verified from inside the game. The thread list is enumerated only when no live main-thread handle is held.
- **Player.log tail**: the file is opened with share-read, share-write and share-delete, so Unity's rename at launch
  is never blocked. Each poll fstats the open handle, so the identity is the file id of what was actually read.
  - Rotation (a new file id) and truncation (size below the last offset) become events.
  - Each poll reads at most 1 MB of new bytes and counts the rest as `skippedBytes`. A brand-new file is read up to
    8 MB once, to find startup landmarks.
  - The file is never reread and never hashed.
- **Startup milestones**: `engine.mono`, `engine.init`, `game.version`, `rimbridge.startup`, `jawabench.ready`,
  `bridge.token`, `unity.memstats`, `log.cap-reached` and `log.cap-lifted`.
  - Each is stamped with its observation time and `precisionS` set to the sample interval.
  - A landmark already in the log when the collector starts is marked `timeUnknown`.

**Readers:**

- `python3 src/RimMandrake/Utils/health_observer.py --read`
- `python3 src/RimMandrake/Utils/tps_record.py --at "<time>" --health` prints the observer's coverage, its events,
  and the nearest observer sample before and after each TPS incident, with no verdict.
- `belt_watchdog.py` CPU trend: it now keys on pid **and** start time and uses a monotonic interval. When the wall
  clock disagrees with that interval, it gives no rate. Its wording no longer claims a "main-thread tight loop" from
  a process total.

### 2. Offline forensics: `src/RimMandrake/Utils/health_forensics.py` (`LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED`)

- **`load-tree <Player.log>`** parses the DeepProfiler tree. The engine prints that tree only when
  `Prefs.LogVerbose` is on.
  - The parser follows the format in `ThreadLocalDeepProfiler.AppendStringRecursive`. The engine **merges
    same-label siblings** into `<n>x label`, so a node is a label group and not a single call.
  - It flags trees that never reached the hotspot table as incomplete and checks that self times sum to the root.
  - It streams line by line and keeps at most 200,000 nodes per tree.
  - **UNMEASURED against real output:** none of the 18 archived logs holds a tree. The search on 2026-10-10 found
    the `Initialize engine version` landmark, which shows it could see the logs. It is tested against a fixture built
    from the decompiled formatter.
  - A verbose load is a diagnostic load. Compare it only with other verbose loads.
- **`save-census <.rws>`** is a streaming iterparse. Every finished element is cleared and detached as soon as it
  ends.
  - It reports things by Class and by def, map count, world-pawn entries, and elements and text characters by
    section path (depth 6 or less).
  - A truncated save is reported as INCOMPLETE.
  - Measured 2026-10-10: the 16.7 MB canonical start save took 0.5 s, and a 49.5 MB save took 1.4 s with a peak RSS
    of 18 MB.

## Contracts (GPT review section 6.4 gates)

Every capability reports **PASS / FAIL / UNMEASURED / UNSUPPORTED** on its own. A partial build never becomes a
global "health capture complete".

| gate | what passes it | state |
|---|---|---|
| Source truth | Each source has a stable id, a question, a status word and a unit in its field name. Unavailable is never 0 (selftest 2, 11) | PASS offline |
| Serialization | `allow_nan=False`, so an unserialisable row becomes an `error` row. Strict seq per collector. The reader counts malformed lines (selftest 4) | PASS offline |
| Interval correctness | CPU rates use monotonic intervals, with no rate across an identity change or a clock that runs backwards. The watchdog refuses a wall/mono disagreement over 2 s | PASS offline; sleep/resume UNMEASURED |
| Histogram correctness | owed (frame histogram, `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD`) | UNMEASURED |
| Logging correctness | Log growth plus `log.cap-reached`, which reads "emission suppressed; error activity unknown". The in-game cap/logger state is owed | external half PASS; in-game owed |
| Harmony safety | owed (`TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS`) | FAIL until fixed (GPT 2.3 hazards stand) |
| Lifecycle | `game-start` and `game-exit` with the exit code, a held handle, and nothing reset at a game change. Seen live 2026-10-10 17:28:13Z, exit code 1 | PASS for one exit; two-process and relaunch cases UNMEASURED |
| Writer isolation | Separate stream, size-rotated segments and retention cap. A blocked disk is not tested | partial |
| Observer truth | Heartbeat with `failedProbes`, `lateS`, `wallMinusMonoS` and `missedDeadlines`. A failed probe is never read as an exit | PASS offline; sleep/resume and PID reuse live UNMEASURED |
| Retention | 14 days, 256 MB. Bytes per day not yet measured over a full day | UNMEASURED |
| Cost | Collector self-cost measured (below). The full-list C0-C5 protocol is owed (`RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP`) | collector MEASURED; in-game UNMEASURED |
| Overnight utility | owed: induced slowdown, exit and relaunch, next-day reconstruction | UNMEASURED |

## Metrics ledger

**Status** is built, owed or unsupported. **Measured cost** is per sample for the observer sources: the median of
`costUs`, from 21 samples taken while a full-list game ran on 2026-10-10 between 17:26 and 17:29 UTC (the game
exited at 17:28:13Z). Over that whole run, which also covered an idle stretch, the collector used **0.00303 cores in
total (0.30 % of one core)**: 0.5 s of CPU in 165 s. The run used the build before the log tail's ctypes binding was
cached, so `log.growth` cost less from then on. **Decommission test** says how to remove the metric cleanly. The owner
fills in **Owner verdict**.

| metric id | status | question it answers | measured cost | decommission test | owner verdict |
|---|---|---|---|---|---|
| `obs.heartbeat` | built | Was the observer running and on time, and what did it cost? | included in the totals | Removed only with the whole observer. Without it, observer gaps are unreadable | |
| `game.identity` | built | Which RimWorld processes ran (pid and creation time), and when did each start and exit, with what exit code? | 7.2 ms median (Toolhelp process snapshot) | Switch off: `game.cpu`/`game.mainthread`/`game.memory` then see no processes, so they go with it | |
| `game.cpu` | built | How many cores did the game process use, across all threads? | 0.02 ms | `--off game.cpu`; no other source reads it except `game.mainthread`'s other-threads figure | |
| `game.mainthread` | built | How many cores did the (assumed) main thread use, and how many did the other threads use? | 0.01 ms steady; 45 ms when it re-enumerates threads (at game start or when the thread exits) | `--off game.mainthread`; nothing reads it | |
| `game.memory` | built | Game working set, peak working set and private bytes | 0.01 ms | `--off game.memory`; nothing reads it | |
| `sys.memory` | built | Is the machine short of physical memory or commit headroom? | 0.13 ms | `--off sys.memory`; nothing reads it | |
| `log.growth` | built | How fast is Player.log growing, and was it truncated or rotated? | 6.0 ms median before the binding cache; 1.4 ms on one sample after | `--off log.growth`, which also leaves `log.milestones` unavailable | |
| `log.milestones` | built | When did the startup landmarks appear, and did Verse.Log hit its cap? | 0.01 ms steady; 23 ms when it scans a new log once | `--off log.milestones`; nothing reads it | |
| `watchdog.cpu-trend` | built (fixed) | Process CPU trend between `belt_watchdog.py` passes | UNMEASURED (rides the existing PowerShell probe) | Delete the `cpu_rate` call in `belt_watchdog.gather` | |
| `forensics.load-tree` | built | Where did a verbose load spend its time, by label group? | UNMEASURED on real data (no tree archived) | Delete `load-tree` from `health_forensics.py`; it is on demand only | |
| `forensics.save-census` | built | What is in a save that makes it big or slow (things by class and def, sections)? | 0.5 s for 16.7 MB, 1.4 s and 18 MB RSS for 49.5 MB | Delete `save-census`; it is on demand only | |
| `forensics.content-identity` | owed | Is this the same mod content, settings and save as last time (reproduction identity)? | UNMEASURED | (not built) | |
| `tps.frame-hist` | owed | What does the frame-interval distribution look like (merged histograms, never averaged p99s)? | UNMEASURED | (not built) | |
| `tps.log-counts` | owed | How many messages were emitted per type, and is the cap or logger suppressing them? | UNMEASURED | (not built) | |
| `tps.bridge-occupancy` | owed | How much main-thread time and queue delay did bridge calls cause (agent load versus owner-only play)? | UNMEASURED | (not built) | |
| `tps.capability-inventory` | owed | Which recorder sources work in this build, and why are the others unavailable? | UNMEASURED | (not built) | |
| `opt.own-counters` | owed | How much do our own mods' hot paths cost? | UNMEASURED | (not built) | |
| `opt.profiler` | owed | On demand and expiring: what does an exact allowlist of methods cost? | UNMEASURED | (not built) | |
| `spike.gc-timing` | owed | Does a GC coincide with a gap (labelled coincidence)? | UNMEASURED | (not built) | |
| `spike.early-load` | owed | Where does a cold load stall before the companion exists? | UNMEASURED | (not built) | |
| `spike.minidump` | owed | What was the process doing during a hang (one capture per incident, headroom checked)? | UNMEASURED | (not built) | |
| `tps.presentation-fps` | unsupported (for now) | Displayed FPS, as opposed to `Root.Update` cadence | UNMEASURED | (not built; needs a presentation-timing source nobody has identified) | |

## Owed, by ticket

| ticket | what | blocked on |
|---|---|---|
| `HEALTH_BANDS_WIRE_QUEUED_BEHIND_OVERHEAD` | Minimal in-game extension: frame-interval histogram, log counts with suppression state, bridge occupancy and queue delay, capability inventory | TPS full-list overhead test (MUST 17) |
| `LOAD_SAVE_FORENSICS_BUILD_NO_GAME_NEEDED` | Remaining: content identity, and a real verbose-load tree to measure the parser against | a verbose launch (Prefs.LogVerbose) archived |
| `OPTIMISATION_TOOLS_BUILD_BY_NAME_NOT_BLAME` | Own-code counters and the on-demand profiler | MUST 17 |
| `GC_EARLYLOAD_DUMPS_PROBE_SHOW_VALUE_FIRST` | GC timing, early-load probe and small dumps, each proven on a known case first | MUST 17 |
| `TPS_HOOKS_HARDEN_REENTRY_AND_LATE_GUARDS` | The companion C# hazards from GPT review 2.3 | the companion is being deployed for the MUST 17 test; do not edit it underneath that test |
| `RECORDER_OVERHEAD_MEASURE_SIX_CONFIGS_DEEP` | Full-list C0-C5 protocol, run over several days | MUST 17 |
| `HEALTH_METRICS_JUDGE_EARN_THEIR_KEEP` | Owner's post-hoc review of this ledger | data from the built sources |
| `GAME_OBSERVER_BUILD_OUTSIDE_LOOKING_IN` | Remaining: install it as a standing task, and measure sleep/resume, two processes, PID reuse and bytes per day | the owner's go-ahead to run it during the overhead test (C1 is its own configuration) |

**Not installed as a standing task yet**, on purpose. Configuration C1 of the overhead protocol is "external collector
only", so the collector must not run unannounced during the MUST 17 measurement. The install line is in the script's
header.

Sources: `Transient/foundry_metrics_design_20261010.md` (Opus, 100 candidates),
`Transient/foundry_metrics_review_gpt_20261010.md` (GPT, sections 2.3, 4.4 and 6.4) and
`Transient/foundry_metrics_combined_20261010.md`. All three are Transient files with a shelf life of about 14 days.
Everything that binds the build is restated above.
