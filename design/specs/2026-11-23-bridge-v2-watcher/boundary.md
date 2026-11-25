# BOUNDARY: game watcher

Code: `src/RimMandrake/Utils/game_watcher.py` (all of it), the `stop --broken` branch of
`src/RimMandrake/Utils/game_instance.py`, the scene admission calls in `src/RimMandrake/Utils/scene.py` and
`src/RimMandrake/Utils/scene_world.py`, and the watcher fields and inputs in
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsWatchdog.cs`,
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchTpsSampler.cs` and
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFirstException.cs`.
Item: `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`. Proof: `src/RimMandrake/Utils/selftest_game_watcher.py`.

## ACCEPTS

One local game name or letter per call. The heartbeat must belong to its sole running process by PID and start time.
The read-only `game_watcher.py <game>` prints the state and evidence as JSON. Exit 0 is a measured nonbroken
state, 1 a broken state or process gone, 2 COULD NOT LOOK, and 3 an unknown or nonlocal game name.
Menu and no map are available for scene setup. The scene gate refuses a game read as broken or gone. On a blind
reading it continues with the scene's normal checks and adds one watcher line to the receipt's `could_not_look`.

## LIMITS

- **Heartbeat freshness and recent tick progress: 15 s.** A stale file can keep a paused flag indefinitely after
  the writer stopped. This is the TPS observer's freshness limit against the writer's 5 s cadence.
- **Frames stopped: 60 s.** A single slow frame can recover; the stall dump already starts at 60 s. The save on
  Grey Sea on 2026-10-08 took 20 minutes and recovered. A save or an unclassified long event needs other evidence.
- **Explicit loading: 600 s.** Real map initialization can run for minutes. The scene library uses 600 s for a map
  that never settles, after the live MapInitializing stall on 2026-10-26 (load r8). Cold startup without an explicit
  map load is outside this decision.
- **Exception streak: at least two consecutive throws spanning 5 s.** A single thrown frame can be followed by a
  healthy frame before the next 5 s watchdog write. FlowWorks session `ee0fbaa8` logged 100 Root.Update exceptions.
  The existing first-exception tap sees these before Verse's log cap, even when the exception stays inside Root.Update.
- **Stop confirmation: 10 s between reads, same PID, start time and session, with an advancing heartbeat sequence
  and at least 5 s between watchdog writes.** The writer normally publishes every 5 s and warms up with two immediate writes. A stale
  paused file or one transient bad frame must never cause a kill. The readings must show the same stall or load,
  or a fault streak covering every completed frame between them.
- **Process-start match: 2 s.** The existing TPS observer allows this spread between its Windows probes. Its PID reuse
  fixture shows why a PID by itself can attach a dead process's heartbeat to a new process.

## PROMISES

- **ticking.** Recent tick progress on an unpaused map reads ticking.
- **paused.** A fresh heartbeat with live frames and a paused map reads paused, also at tick zero.
- **frames-stopped.** The live writer can observe a stopped main thread. Only a confirmed episode authorizes a stop,
  and the stop result names the game, reason and evidence. The emergency path requires the full `--broken` option.
  Ordinary stop keeps its help, argument errors, hold and bridge checks, taskkill arguments, output and exit codes
  (`t_ordinary_stop_matches_parent`).
- **frame-exceptions.** A sustained streak of Root.Update exceptions, thrown or reported by Verse in the frame, is
  distinguished from stopped frames.
- **stuck-load.** A lasting explicit load reads stuck load. An ordinary load in progress does not authorize a stop.
- **menu.** A responsive entry scene is distinguished from a world with no current map.
- **no-map.** A responsive world with no current map reads no map.
- **process-gone.** An empty measured process list means the named process is gone.
- **never-start-on-a-broken-game.** The real scene entry points refuse before connecting or asking a run hand to start.
  Each admission check reads the process list and heartbeat without a bridge call.
- **could-not-look.** A missing, unreadable, stale, unowned or incomplete heartbeat stays distinct from ticking or paused.
  The deployed heartbeat shape, a missing heartbeat and unreadable bytes each leave `scene.open` and `s.run` unchanged
  apart from one watcher line in the returned and saved receipt (`t_blind_admission_records_once`).

## DOES NOT SURVIVE

- **a-dead-watchdog-or-unreadable-process-list.** No stop is authorized on blind evidence.
- **an-exception-swallowed-silently.** The watcher sees exceptions that escape Root.Update or that Verse reports as
  root-level exceptions. Errors elsewhere in Unity and a missing log hook reduce exception coverage.

`rm-game-watch.timer` reads each local game (including ArchBig) every 2 minutes and routes a broken reading to the same
stop ([its page](../2026-11-24-game-watch-tick/boundary.md)). The verb confirms again and returns the result for reporting.
The stop verb returns 0 for a successful stop, 1 for a stop failure, 2 for a blind reading and 3 for a refusal.
Keep the named game's Player.log and existing stall dump with the report. The watcher owns no timer or state file.
