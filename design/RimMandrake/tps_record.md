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
| low ratio, `sim` high (> ~0.6), `top tl:Normal 70%` | hypothesis: simulation-bound (thing ticks dominate). Elapsed scope time, so CPU starvation or GC look the same - check `attrValid` |
| low ratio, `sim` low, `fps` low | hypothesis: frame-bound (rendering / UI / outside ticks). At high speed the engine's 2 × mult ticks-per-frame cap makes TPS follow FPS |
| `stall` window + `INCIDENT stall` | the main thread stopped for `gapS`; `blocked in` = where (the watchdog's `quietPhase`), `recovered in` = the phase after |
| `longevent` window + `INCIDENT longevent` | an identified save or long event (map gen, autosave) |
| `SILENCE` lines | the watchdog thread saw no main-thread frame for > 10 s; a permanent hang ends here |
| `paused` / `mixed` | recorded, never judged |
| `-- NO COVERAGE --` | no sampler, game down, at the menu, or a writer gap. **Never** "TPS was fine" |
| `OBSERVER exited-without-shutdown` | the process died (crash/kill); its record ends at the main thread's last progress (`lastMainProgressUtc`) |
| `OBSERVER hb-stale-alive` | the same process still runs but its heartbeat stopped: suspension, watchdog stopped, disk, debugger or sleep - cause not established |
| `OBSERVER shutdown-incomplete` | a shutdown started but its drain/log copy did not finish |

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
| observer findings | `observer.jsonl`, appended by `belt_watchdog.py` from outside the game (open / update / ended); outside retention, a few rows a day |
| Player.log archive | `tps\logs\Player-prev_<mtime>_<sha12>.log` (the previous session: copied by every `belt_watchdog.py` pass and at companion start, deduplicated by content hash), `Player_<utc>_<session>_<sha12>.log` at clean shutdown |
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

Retention: a session is **active** while its heartbeat file is under 60 s old (the heartbeat is its lease).
Inactive sessions are deleted as whole **bundles** (segments, heartbeat and manifest together): first those
whose newest file is older than 7 days, then — only while the directory exceeds 256 MB — the oldest
bundles. So an inactive session is kept 7 days **unless the cap forces it out earlier**. Never deleted:
any file of another active process, this process's live segment, heartbeat and manifest; this process's
own closed segments go oldest-first only when it alone exceeds the cap. Archived logs: same age rule,
1 GB cap. A window line with attribution is ~1-2 KB (the old ~300 B estimate ignored the attribution
fields), so a day of continuous play is tens of MB.

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
observes paused/multiplier **before** tick work; after the tick work the sampler adds that invocation's
duration and ticks. A window is the real time **between two prefix observations**, `[monoStart, monoEnd]`,
and is closed in the prefix, **before** that frame's tick work. So it holds every interval between its
prefixes and every tick invocation that **started** inside it: its tick work (`simMs`, attribution)
physically lies inside its own `dReal` (`simShare` ≤ 1), and a long tick lands in the same window as the
gap it causes. The engine credits a frame's real time to that frame's ticks, so tick counts can lag the
real-time boundary by one frame (≤ 2 × mult ticks). The reader places a window by its boundaries
(`utc − (mono − monoStart) .. utc − (mono − monoEnd)`), never by when it was written.

Per interval: paused → paused seconds; running → `expected += 60 × mult × interval`; identified time
(`explained`, below) → excluded from expected and counted separately. An **unexplained gap across a
pause/speed change** is ambiguous: it stays in `expected` at the **high** end of the two states,
`expectedLo` carries the low end and `ratioHi = dTicks / expectedLo` the other bound (null when the low end
is a pause). A multiplier change inside the tick loop is also ambiguous. A tick counter that goes
backwards is flagged `tickReset`, never silently clamped.

| field | meaning |
|---|---|
| `seq`, `v`, `utc`, `mono`, `session`, `kind` | on every line: writer order, schema version (2), wall time (ms), process-monotonic seconds, session id |
| `monoStart`, `monoEnd` | the window's explicit boundaries (monotonic seconds) |
| `game` | 1, 2, … per game entered in this process: rows of two games are never joined |
| `state` | `run`, `paused` (≥ 50 % of the window's **time** paused), `mixed` (ambiguous ≥ 25 % of running time), `stall` (unexplained gaps ≥ 50 %), `longevent` (explained ≥ 50 %) |
| `ratio` | `dTicks / expected`. **This is the number to judge.** null when nothing was expected |
| `expectedLo`, `ratioHi` | the other end of the range when a gap crossed a state change (equal to `expected`/`ratio` otherwise) |
| `tps` / `tpsWall` / `target` | ticks per running second / per wall second / time-weighted `60 × mult` |
| `dReal`, `runS`, `pausedS`, `explainedS`, `stallS`, `ambigS` | where the window's seconds went |
| `multMin`, `multMax`, `mult`, `transitions` | effective multiplier range (Superfast is 6 or 12 depending on `NothingHappeningInGame`; forced-normal is 1), end value, state changes |
| `frames`, `fps`, `gapMaxMs`, `gaps` | frames, frame rate, the longest frame interval (Stopwatch, unclamped), gap incidents |
| `simMs`, `simMaxMs`, `simShare` | time inside `TickManagerUpdate` of invocations started in the window |
| `capFrames`, `budgetFrames` | frames that hit the 2 × mult tick cap / exceeded the ~45 ms tick budget. Indicators, not proof the cap or budget stopped progress |
| `tickReset` | the tick counter went backwards inside the window |
| `tickMs` | the engine's own `MeanTickTime`, a lagged EMA. Context only, never attribution |
| `attr`, `top`, `worst`, `attrValid`, `attrOverMs`, `profSkipped`, `profHooks`, `profEstMs` | attribution, below |
| `focused`, `gc`, `heapMB` | focus, GC collection count (Unity's Boehm GC has no generations), managed heap |
| `wq`, `wfly`, `wdrop`, `wdropCrit`, `werr`, `wtorn` | writer: all outstanding lines (incl. in flight), in flight, dropped, dropped critical rows, write errors, torn tails repaired |

**Explained time** is the **union of measured intervals** of identified work, taken against each
observation interval: `LongEventHandler.LongEventsUpdate` while an event is running (a synchronous event,
e.g. autosave, runs inside it), every `GameDataSaveLoader.SaveGame` (a direct save by a mod outside any
long event included; a save nested in a long event counts once), and whole frames where
`ShouldWaitForEvent` held (an asynchronous event, e.g. map generation, during which `UpdatePlay` does not
run). Scopes open in a prefix and close in a Harmony **finalizer**, so an exception cannot leave one open;
an open scope is split at an observation, never credited twice. Only that is excluded.
⛔ **Unexplained gaps are never subtracted**: a 90 s freeze stays in expected ticks (also across a state
change, at the high end), makes a `stall` window with a tiny ratio, and is an incident.

## Other line kinds

| kind | when |
|---|---|
| `session` | sampler start: pid, `startedBy`, build, engine, mod count, `modDigest` (sorted ids) and `modOrderDigest` (ordered `id@version`), Player.log path, settings + `settingsNote`, `install{}` (sampler / attribution status and per-target detail, watchdog) |
| `marker` | start, each game entered, hourly. The same `session` and `seq` go to Player.log as `[JawaBench] TPS marker` (`DROPPED` when the writer was full), which joins the log to the record |
| `game` / `menu` | a game was entered (`game` seq; `save` = the load request it came from, "" for a new game) / left |
| `incident` | a frame gap > 2 s: `type` `stall` or `longevent`, `game`, `gapS`, `explainedS`, `unexplainedS`, `ambiguous`, `multAfter` (observed after the gap) and `mult` (cached before it), `quietPhase` (where the watchdog saw the main thread BLOCKED), `phase` (where it recovered), `prevSimS`, `gcDelta`, save state, ticks, speed, pause, focus, heap, writer health. Spans its gap: a query inside the gap selects it |
| `context` | every 60 s of play: per map (≤ 8) id, size, biome, spawned pawns, things, current; world pawns; heap; process working set; save |
| `save` | each `GameDataSaveLoader.SaveGame`: file, seconds, `threw` when it threw |
| `silence` / `resumed` | watchdog thread: main thread silent > 10 s (repeated every 30 s while it lasts) / it came back (spans the silence) |
| `shutdown` / `shutdown-complete` | `Application.quitting`: the INTENT row, then the drain (2 s), the Player.log copy (3 s, its own thread) and a completion row stating `drained`, `archived`, `archiveTimedOut`, `ms`. Only both together are a clean end |
| `dropped` | the writer dropped rows: `count`, `seqFirst..seqLast`, totals. Written once it catches up |
| `error` | the sampler or a hook disabled itself after an exception, an install failed (rolled back), or a manifest/log-archive step failed |
| `log` | a Player.log was archived: path, `sha256`, `bytes`, `fromSession` |
| `observer` | from `belt_watchdog.py` (outside the process): `silent`, `hb-stale-alive`, `hb-stale-unknown`, `shutdown-incomplete`, `exited-without-shutdown`, each with `state` open / update / ended |

## Attribution

Prefix + **finalizer** timers on the coarse stages of `TickManager.DoSingleTick`: the whole tick, the three
tick lists (by the list's own `tickType`), `World.WorldTick`, `World.WorldPostTick`, `Map.MapPreTick`,
`Map.MapPostTick`, `MapComponentUtility.MapComponentTick` (nested inside `MapPostTick`) and
`GameComponentUtility.GameComponentTick`. Per window, `attr` gives `[count, total ms, max ms]` for each,
**inclusive**. `top` is the largest **exclusive** stage as a share of tick time (`tickOther` = storyteller,
quests, letters, history and the rest of `DoSingleTick`). `attrValid: false` (+ `attrOverMs`) when children
exceed their parent - the assumed call tree did not hold (overlap, recursion, a timer outside its parent)
and the exclusive split is not to be read. `worst` holds up to 3 single ticks ≥ 30 ms with their tick id,
duration (the same one the total got) and a numeric exclusive `stages{}` breakdown. Totals and worst ticks
reset at every game boundary.

Hooks are contained: an exception in a hook disables attribution (`attrError`, the tool's
`attribution.runtimeError`) and never reaches the tick; a finalizer whose prefix did not run, or a hook on
a non-main thread, records nothing (`profSkipped`). On the installed Harmony 2.4.2 our void `out __state`
prefixes are never skipped by another prefix returning false (decompiled `MethodCreator.AffectsOriginal`);
the guard exists because that is version behaviour.

⚖️ Overhead: `profHooks` timer pairs fired × the per-pair cost calibrated at install = `profEstMs`. That is
an **incomplete estimator, not a bound**: it omits Harmony dispatch, the phase stack and the finalizer
blocks, and calibration noise can also inflate it. The real cost is owed from three separately restarted
configurations on the full list (sampler off / sampler without attribution / full) — criterion C4 below.
`"attribution": false` switches it off without touching the windows.

⚠️ **"Why" is a lead, not a verdict.** A stage's time is elapsed residence in that scope: CPU, scheduler
deprivation, GC suspension and blocking I/O all count. The reading table's "simulation-bound" /
"frame-bound" lines are hypotheses to check, and `session_<id>.json`'s `patchChains` (owner, kind,
priority and patch method on each measured target) are candidate evidence, not a culprit list.
⛔ Per-method, per-pawn and per-mod instrumentation stays out of the always-on path (ruled SKIP).

## The watchdog thread and the external observer

The main thread stamps a heartbeat at the start of every `Root.Update` (menu and play) and keeps a stack
of coarse phases (`update`, `longEvent`, `save`, `load`, `tickUpdate`, `tick`, `tl:Normal|Rare|Long`,
`world`, `worldPost`, `mapPre`, `mapPost`, `mapComp`, `gameComp`, `frame-rest` = the rest of the frame,
non-tick play update, GUI and rendering, `menu`). A background thread writes `silence` lines and the
`hb_<session>.json` heartbeat. It touches no Unity API.

The heartbeat states two different facts: **`mainBeatUtc` / `mainBeatMono`** — the main thread's last
progress — and **`watchdogUtc` / `watchdogMono`** — when the watchdog thread wrote. It also carries
`hbSeq`, `ticksGame`, `procStartUtc` and `hbErrors` / `hbLastError`, and is published atomically (temp file,
then replace). During a main-thread hang the heartbeat keeps advancing; `mainBeatUtc` does not.

`belt_watchdog.py` is the **external observer**. It matches each `hb_` file against **every** running
`RimWorldWin64` by pid **and start time** (a reused pid is a different process) and reports `silent`
(main thread quiet, process alive), `hb-stale-alive` (that same process runs but its heartbeat stopped:
a whole-process suspension, a stopped or starved watchdog thread, a blocked disk, a debugger or machine
sleep — **cause not established**), `hb-stale-unknown` (the process probe failed: nothing is declared
exited), `shutdown-incomplete` (intent without completion) or `exited-without-shutdown`. Every finding is
appended to `observer.jsonl` when it opens, every 5 minutes while it lasts, and when it ends (terminal
findings once). Each pass also copies `Player-prev.log` into `tps\logs` by content hash before a relaunch
can rotate it. Silence means "no observed main-thread progress", never proven deadlock.

**Standing observer:** `src/RimMandrake/Utils/tps_observer.py` does the same observer pass on its own, every
2 minutes, from the Windows scheduled task `RimMandrake\TPS Observer` (`pythonw.exe` on the
`D:\Luke\dev\RimMandrake` mirror: no console window, no PowerShell; the process probe is Toolhelp +
`GetProcessTimes`, so start times are real). Each pass rewrites `tps\observer_last.json` (time, games seen,
findings, `ok`/`error`) — if that file is old, the standing observer is not running. Install/remove lines are
in the script's header. The task is Windows state, not in git: re-create it on a rebuilt machine.

## Durability

One writer thread. Every line gets its `seq` at enqueue, so file order is event order across threads. The
bound (4,096 lines) is on **all outstanding work — queued, awaiting retry and in flight**; bulk rows
(`sample`, `context`, `marker`) may use 3,584 of it, the rest is reserved for lifecycle, incident, silence and
error rows. A dropped row keeps its `seq` (a visible gap the reader counts as `seq missing`), is counted
(`wdrop`, `wdropCrit`) and reported in a `dropped` row with its seq range once the writer catches up. Writes
are **commit-aware**: a failed batch retries only the lines not yet appended, and before each append the
file is reconciled with the committed length — a torn tail is truncated (fallback: a newline isolates the
fragment as one malformed line), `wtorn` counted. The reader reads a repeated `(session, seq)` once
(`replayed`) and counts a different row under the same key (`conflicts`).

Each batch is written and the file closed. A killed or crashed game loses the lines still queued **and any
in flight**; how long that is under a stalled disk or a starved writer is **unmeasured** (C3). An OS crash
or power cut can still lose the OS cache. A full segment is closed and the next number opened: rotation
never moves, renames or deletes a file holding history, and two processes never share a file.

## Settings

The companion is not a mod and has no settings screen, so the Mod Settings rule is met by
`JawaBench\tps\tps_settings.json`, written with the shipped defaults on first start. It is **read once, at
game launch**: a change takes effect at the next launch. It must be one flat JSON object; a duplicate key,
a nested value, a truncated document or number, a non-finite number or a wrong type makes the whole file
invalid — the shipped defaults are used and the reason is in the `session` row's `settingsNote`.

| key | default | effect |
|---|---|---|
| `sampler` | true | false = no record at all (stated in the Player.log and by the tool) |
| `attribution` | true | the stage timers |
| `watchdog` | true | the silence thread and heartbeat file (without it the external observer is blind) |
| `archivePlayerLog` | true | copy Player-prev.log at start and Player.log at shutdown into `tps\logs` |
| `retentionDays` | 7 | can only be raised (a lower value is raised and noted) |
| `retentionMB` / `logRetentionMB` | 256 / 1024 | byte caps; can only be raised |

## Judgement (watchdog and tool)

- Each game **session is judged on its own rows**; the verdict is the session with the newest window, and
  every other session is listed with its own coverage and sustained state (another live session's
  sustained low/high is reported, never blended in).
- The verdict states **coverage** first: `MISSING` (no record), `STALE` (newest window older than 60 s: game
  down, at the menu, or the sampler stopped; never a performance verdict), `ERROR` (writer errors).
- **SUSTAINED LOW / HIGH** (WARN): the last 6 windows of an **unbroken** streak of fresh `run` windows all
  have `ratio < 0.6` / `> 1.15`, judged on the 3-decimal value the disk carries (the live tool rounds the
  same way). Unbroken means: same session, same `game`, each window starting where the previous ended
  (`monoStart` within 0.5 s of `monoEnd`), no game/menu/error/silence/resumed/shutdown row and no `seq` gap
  in between. One missing window breaks it. The tool's `sustained` reads `unknown` once its newest window
  is over 60 s old.
- A verdict names recovered stalls (count, worst unexplained seconds) even when TPS is otherwise OK.
- TPS is reported **per target** (`target 60: …, target 180: …`), never as one median against the last
  window's target.
- The `tps` and `tps-observer` lines **never change the watchdog's overall verdict**: slow is not hung.

## Acceptance (BRIDGE_TPS_CAPTURE_FIXES_1 C3/C4, rewritten after the second GPT review)

A pass needs the record itself — files read directly, never a bridge answer alone — to show each item:

1. **Autostart without assistance** (C3): a cold launch with no bridge client, no `tps_report` call and no
   bridge-enabled watchdog probe writes a `session` row (`startedBy: bridge-registration`,
   `install.sampler: complete`), menu heartbeats and gameplay windows; repeated for a new game and for a
   save load, each with its own `game` seq and the right `save` label.
2. **Controlled interruption matrix** (C3, disposable state, minimal list allowed): 2–10 s hitches and 40 s
   / 90 s main-thread blocks each appear as ONE `incident` with `kind: incident` (strict JSON parse, no
   duplicate keys), the right `gapS`, a `blocked in` phase, local time with offset, `game` id, and a window
   whose `[monoStart, monoEnd]` contains the gap and its tick work (`simShare` ≤ 1); a save is a
   `longevent`; a permanent hang plus kill leaves `silence` rows, a heartbeat whose `mainBeatUtc` stops
   while `watchdogUtc` advances, and an `exited-without-shutdown` observer row that is still on disk the
   next day; forced kills near sample/segment boundaries leave no replayed or glued rows (`replayed`,
   `conflicts`, `malformed` from the torn tail only).
3. **Environmental discrimination** (C4): focus loss, sleep/resume, CPU and disk competition and two game
   processes produce qualified labels (`hb-stale-alive`, never "whole process frozen" or "mod stall" by
   inference), and neither process's retention touches the other's files.
4. **Overhead** (C4, the full ~600-mod list): three separately restarted configurations — sampler off,
   sampler without attribution, full recorder — on the same save and workload, counterbalanced after a
   warm-up, acceptance limits declared first; fixed-tick completion time, wall TPS, frame-time
   distribution, allocations/GC and recorder I/O, at normal play and at high speed on a demanding colony.
5. **Overnight reconstruction** (C4): recorder left running, a documented slowdown induced, shutdown and
   relaunch; next morning `tps_record.py --at` returns the right game, local time with offset, interval,
   duration, ratios, attribution validity, map identity and the linked archived log.

C3 and C4 cannot pass while any selftest of `selftest_tps_record.py` fails (Python checks, C#/Python
parity and the C# unit group run against the production files).
