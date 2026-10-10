# The TPS record — TPS is measured all the time

Items: `BRIDGE_TPS_REGULAR_REPORT_1` (first build), `BRIDGE_TPS_CAPTURE_FIXES_1` (rebuild after the Opus
and GPT reviews). Owner, 2026-10-10: he regularly sees very slow (and fast) TPS, and agents asked to
investigate later say they cannot reproduce it. So TPS is a standing measurement, not an investigation,
and the record must answer **"was it slow at 3 pm yesterday, and why"**.

## Answering "was it slow at T"

```
python3 src/RimMandrake/Utils/tps_record.py --at "yesterday 15:00"                 # 10 min either side
python3 src/RimMandrake/Utils/tps_record.py --at "2026-10-09 21:30" --span 30m
python3 src/RimMandrake/Utils/tps_record.py --since "today 09:00" --until "today 12:00"
python3 src/RimMandrake/Utils/tps_record.py --sessions                             # which game processes, when
python3 src/RimMandrake/Utils/tps_record.py --session 3f2a --at ...                # one session only
python3 src/RimMandrake/Utils/tps_record.py                                        # verdict over the last 5 min
```

Times you type are read in `--tz` (default `America/Los_Angeles`, his zone; `TPS_TZ` overrides) unless
they carry a zone; the record is UTC and the timeline prints local time. It runs from WSL and reads the
files directly, so it needs no bridge and works with the game down.

The timeline prints every window, every incident, and every **NO COVERAGE** hole. Read it like this:

| you see | it means |
|---|---|
| `run` windows with `ratio` < 0.6 | slow. Check `sim` (tick-work share of the window) and `top` |
| low ratio, `sim` high (> ~0.6), `top tl:Normal 70%` | simulation-bound: thing ticks (pawns, buildings) dominate |
| low ratio, `sim` low, `fps` low | frame-bound: rendering / UI / something outside ticks. At high speed the engine's 2 × mult ticks-per-frame cap makes TPS follow FPS |
| `stall` window + `INCIDENT stall` | the main thread stopped for `gapS`; `quietPhase` / `phase` say where |
| `longevent` window + `INCIDENT longevent` | an identified save or long event (map gen, autosave) |
| `SILENCE` lines | the watchdog thread saw no main-thread frame for > 10 s; a permanent hang ends here |
| `paused` / `mixed` | recorded, never judged |
| `-- NO COVERAGE --` | no sampler, game down, at the menu, or a writer gap. **Never** "TPS was fine" |
| `OBSERVER exited-without-shutdown` | the process died (crash/kill); its record ends at the last heartbeat |

🔑 **Judge `ratio`, never `tps` against 60.** `ratio = dTicks / expected`, where expected ticks are
integrated **frame by frame** at the effective multiplier over **unpaused** time. 170 TPS is healthy at
speed 3 and dire at speed 4, and a window paused 40 % of the time is not "slow".

## Where it lives

| what | where |
|---|---|
| the record (outside git) | `C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\JawaBench\tps\` |
| segments | `tps_<startUtc>_<session>_<pid>_<seg>.jsonl`, a new segment every 2 MB |
| session manifest | `session_<session>.json`: ordered mod packageIds, Harmony patch owners and counts, build, engine |
| heartbeat | `hb_<session>.json`, rewritten every 5 s by the watchdog thread |
| observer findings | `observer.jsonl`, appended by `belt_watchdog.py` from outside the game |
| Player.log archive | `tps\logs\Player-prev_<mtime>.log` at each start (= the previous session, so a crash's log survives), `Player_<utc>_<session>.log` at clean shutdown |
| settings | `tps\tps_settings.json` (below) |
| sampler | `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsSampler.cs` (+ `JawaBenchTpsTools`, the starter) |
| window maths | `JawaBenchTpsMath.cs` (pure; Python port in `src/RimMandrake/Utils/tps_record.py`) |
| writer | `JawaBenchTpsWriter.cs` |
| heartbeat / silence watchdog | `JawaBenchTpsWatchdog.cs` |
| attribution | `JawaBenchTpsProfiler.cs` |
| reader | `src/RimMandrake/Utils/tps_record.py` |
| offline selftest | `python3 src/RimMandrake/Utils/selftest_tps_record.py`: frame traces, the reader, then the production C# built via winbuild (`bridgetools/TpsMathSelfTest`) with every answer compared line for line |
| live tool | `jawa/tps_report` (in-memory last hour + writer, watchdog and attribution health) |
| watchdog lines | `python3 src/RimMandrake/Utils/belt_watchdog.py`: `tps` (coverage, then performance) and `tps-observer` |

Retention: segment, heartbeat and manifest files are kept **at least 7 days**; only if the directory then
exceeds 256 MB do the oldest go first (archived logs: 1 GB). A current-session file is never deleted.
At ~300 bytes a window, a day of continuous play is ~5 MB.

## What starts it

`JawaBenchTpsTools` declares `jawa/tps_report` as an **instance** tool and has a public parameterless
constructor. When RimBridgeServer registers companions after play data loads (decompiled 2026-10-10:
`Root_Update_Patch` → `RimBridgeStartup.OnRuntimeReady` → `RimBridgeCapabilities.Initialize` →
`RimBridgeExtensionDiscovery.BuildProviders` → `TryCreateInstance` → `Activator.CreateInstance`), it
constructs that type, and the constructor starts the sampler. So the record starts at the main menu of
every launch with `brrainz.rimbridgeserver` active, **with no bridge call**. The `session` line says
`startedBy: bridge-registration`; `tool-call` would mean the host never constructed it.

Side effect, deliberate: the constructor is the first code run in the companion module, so the
`JawaBenchInit` module initializer (init lines, arg guard, log suppressor, event recorder) now also fires
at load rather than on the first `jawa/` call.

⛔ Keep that tool an instance method and that constructor public, parameterless and non-throwing. Make
the tool static and the record goes back to starting only on the first `jawa/` call.

## One window

Built by `JawaBenchTpsMath.FrameAccumulator`. A Harmony **prefix** on `TickManager.TickManagerUpdate`
observes paused/multiplier **before** tick work, and the **postfix** reads the ticks done. The engine
credits a frame's real time only when not paused, ticks at the multiplier it reads that frame, and zeroes
unspent credit, so the interval between two prefixes is ticked under the later prefix's state. Per
interval: paused → paused seconds; running → `expected += 60 × mult × interval`; identified long-event
time (`explained`, below) → excluded from expected and counted separately; a change of state across a
blocked gap, or a multiplier change inside the tick loop → **ambiguous** seconds.

| field | meaning |
|---|---|
| `seq`, `utc`, `mono`, `session`, `kind` | on every line: writer order, wall time (ms), process-monotonic seconds, session id |
| `state` | `run`, `paused` (≥ 50 % of the window's **time** paused), `mixed` (ambiguous ≥ 25 % of running time), `stall` (unexplained gaps ≥ 50 %), `longevent` (explained ≥ 50 %) |
| `ratio` | `dTicks / expected`. **This is the number to judge.** null when nothing was expected |
| `tps` / `tpsWall` / `target` | ticks per running second / per wall second / time-weighted `60 × mult` |
| `dReal`, `runS`, `pausedS`, `explainedS`, `stallS`, `ambigS` | where the window's seconds went |
| `multMin`, `multMax`, `mult`, `transitions` | effective multiplier range (Superfast is 6 or 12 depending on `NothingHappeningInGame`; forced-normal is 1), end value, state changes |
| `frames`, `fps`, `gapMaxMs`, `gaps` | frames, frame rate, the longest frame interval (Stopwatch, unclamped), gap incidents |
| `simMs`, `simMaxMs`, `simShare` | time inside `TickManagerUpdate` (tick work plus its loop) |
| `capFrames`, `budgetFrames` | frames that hit the 2 × mult tick cap / exceeded the ~45 ms tick budget. Indicators, not proof the cap or budget stopped progress |
| `tickMs` | the engine's own `MeanTickTime`, a lagged EMA. Context only, never attribution |
| `attr`, `top`, `worst`, `profHooks`, `profEstMs` | attribution, below |
| `focused`, `gc`, `heapMB`, `wq`, `wdrop`, `werr` | focus, GC collection count (Unity's Boehm GC has no generations), managed heap, writer queue/drops/errors |

**Explained time** = time inside `LongEventHandler.LongEventsUpdate` while an event is running (a
synchronous event, e.g. autosave, runs inside it) plus whole frames where `ShouldWaitForEvent` held (an
asynchronous event, e.g. map generation, during which `UpdatePlay` does not run). Only that is excluded.
⛔ **Unexplained gaps are never subtracted**: a 90 s freeze stays in expected ticks, makes a `stall`
window with a tiny ratio, and is an incident. There is no 60 s discard any more.

## Other line kinds

| kind | when |
|---|---|
| `session` | sampler start: pid, `startedBy`, build, engine, mod count + digest, Player.log path, settings |
| `marker` | start, each game entered, hourly. The same `session` and `seq` go to Player.log as `[JawaBench] TPS marker`, which joins the log to the record |
| `game` / `menu` | a game was entered (save name if loaded from a file) / left |
| `incident` | a frame gap > 2 s: `type` `stall` or `longevent`, `gapS`, `explainedS`, `unexplainedS`, `ambiguous`, `quietPhase` (the phase the watchdog saw during it), `prevSimS`, `gcDelta`, save state, last phase, ticks, speed, pause, focus, heap, writer health |
| `context` | every 60 s of play: per map (≤ 8) id, size, biome, spawned pawns, things, current; world pawns; heap; process working set; save |
| `save` | each `GameDataSaveLoader.SaveGame`: file and seconds |
| `silence` / `resumed` | watchdog thread: main thread silent > 10 s (repeated every 30 s while it lasts) / it came back |
| `shutdown` | `Application.quitting`; the writer is then drained (2 s bound) and Player.log archived |
| `error` | the sampler disabled itself after an exception, or a manifest/log-archive step failed |
| `log` | a Player.log was archived |
| `observer` | from `belt_watchdog.py` (outside the process): `silent`, `frozen`, `exited-without-shutdown` |

## Attribution

Prefix/postfix timers on the coarse stages of `TickManager.DoSingleTick`: the whole tick, the three tick
lists (by the list's own `tickType`), `World.WorldTick`, `World.WorldPostTick`, `Map.MapPreTick`,
`Map.MapPostTick`, `MapComponentUtility.MapComponentTick` (nested inside `MapPostTick`) and
`GameComponentUtility.GameComponentTick`. Per window, `attr` gives `[count, total ms, max ms]` for each,
**inclusive**. `top` is the largest **exclusive** stage as a share of tick time (`tickOther` = storyteller,
quests, letters, history and the rest of `DoSingleTick`). `worst` holds up to 3 single ticks ≥ 30 ms with
their own `top`. Save time is timed separately (`save` lines, `saveTotalS` on incidents).

⚖️ Overhead: `profHooks` timer pairs fired × the per-pair cost calibrated at install = `profEstMs`. That
is a **lower bound** (Harmony trampolines are not in the calibration). The real cost on the full ~600-mod
list is owed from a live A/B (criterion C3). `"attribution": false` switches it off without touching
the windows.

⛔ Per-method, per-pawn and per-mod instrumentation stays out of the always-on path (ruled SKIP). Which mod
owns a hot stage is a targeted follow-up, using `session_<id>.json`'s Harmony owners as the candidate list.

## The watchdog thread and the external observer

The main thread stamps a heartbeat at the start of every `Root.Update` (menu and play) and keeps a stack
of coarse phases (`update`, `longEvent`, `save`, `load`, `tickUpdate`, `tick`, `tl:Normal|Rare|Long`,
`world`, `worldPost`, `mapPre`, `mapPost`, `mapComp`, `gameComp`, `frame-rest` = the rest of the frame,
non-tick play update, GUI and rendering, `menu`). A background thread writes `silence` lines and the
`hb_<session>.json` heartbeat. It touches no Unity API.

A managed thread cannot run during a stop-the-world GC or a native hang, and nothing inside a dead process
can write. So `belt_watchdog.py` is the **external observer**: it compares each `hb_` file's age and
`silentS` with the live `RimWorldWin64` pid and reports `silent` (main thread quiet, process alive),
`frozen` (pid running, heartbeat file stopped: whole process suspended) or `exited-without-shutdown` (pid
gone, no `shutdown` line: crash or kill), appending each finding once to `observer.jsonl`. Silence means
"no observed progress", never proven deadlock.

## Durability

One writer thread, one bounded queue (4,096 lines). Every line gets its `seq` at enqueue, so file order is
event order across threads. Each batch is written and the file closed, so it sits in the OS cache when the
batch ends: a killed or crashed game loses at most the lines still queued (normally under a second). An
OS crash or power cut can still lose the OS cache. A full queue drops and counts (`wdrop`) rather than
block the game; a failed write is retried and counted (`werr`). A full segment is closed and the next
number opened: no file holding history is ever moved, renamed or deleted by rotation, and two game
processes never share a file.

## Settings

The companion is not a mod and has no settings screen, so the Mod Settings rule is met by
`JawaBench\tps\tps_settings.json`, written with the shipped defaults on first start:

| key | default | effect |
|---|---|---|
| `sampler` | true | false = no record at all (stated in the Player.log and by the tool) |
| `attribution` | true | the stage timers |
| `watchdog` | true | the silence thread and heartbeat file (without it the external observer is blind) |
| `archivePlayerLog` | true | copy Player-prev.log at start and Player.log at shutdown into `tps\logs` |
| `retentionDays` | 7 | can only be raised |
| `retentionMB` / `logRetentionMB` | 256 / 1024 | byte caps, applied after the age rule |

## Judgement (watchdog and tool)

- The verdict states **coverage** first: `MISSING` (no record), `STALE` (newest window older than 60 s: game
  down, at the menu, or the sampler stopped; never a performance verdict), `ERROR` (writer errors).
- **SUSTAINED LOW / HIGH** (WARN): the last 6 windows of an **unbroken** streak of fresh `run` windows all
  have `ratio < 0.6` / `> 1.15`. A paused or mixed window, a new session, or a coverage hole restarts the
  streak.
- TPS is reported **per target** (`target 60: …, target 180: …`), never as one median against the last
  window's target.
- The `tps` and `tps-observer` lines **never change the watchdog's overall verdict**: slow is not hung.
