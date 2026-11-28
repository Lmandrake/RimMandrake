# BOUNDARY: a game that we launch opens behind his windows and takes no focus, Design Version 0.1.0

Code: `src/RimMandrake/Utils/launch_behind.py` (all of it); `src/RimMandrake/Utils/game_instance.py` (`fire_a`,
`_fire_a`, `_launch_a`, `launch`, `_launch_named`, and `--front` in `main`).
Item: `RIMMANDRAKE_LAUNCH_GAME_BEHIND_HIS_WINDOWS_IT_STEALS_FOCUS`, written 2026-11-27. The owner, that night: "When you
launch Rimworld for testing, can you launch it not as the most foreground window? It's very distracting to have it steal
focus and be in front all the time."
Each promise has a test of its name in `src/RimMandrake/Utils/selftest_launch_behind.py`, which also runs the path
promise on planted faults and fails unless each fault turns it red. The live behaviour is tested by
`src/RimMandrake/Utils/focus_probe.py` (section LIVE). This page covers only these parts of the files named.

## ACCEPTS (the only inputs this is built for)

- **a-launch-on-archmagi.** A start of ArchBig (Steam's URL, or the direct start when Steam will not) or of a named game
  (ArchSmall) through `game_instance.launch` or `game_instance.fire_a`, from WSL, with `powershell.exe` and WMI
  (`Win32_Process.Create`) reachable.
- **a-front-reason.** `front="<reason>"` on `launch` / `fire_a`, `--front "<reason>"` on the CLI, or
  `RM_LAUNCH_FRONT="<reason>"` in the environment. Any non-blank text is a reason.

## DOES NOT SURVIVE (not promised)

- **steve-desktop.** `infrastructure/stevedesktop/rw_game.sh` starts Steve1 and Steve2 its own way. Nothing here touches
  those games.
- **a-flicker-of-milliseconds.** Windows fires a foreground event for a new game window even when the start does not
  activate it, and Steam's "Launching..." window takes the foreground for a moment. The guard undoes each within about
  0 to 30 ms (MEASURED 2026-11-27). A keystroke that he types inside those milliseconds can reach the game. The probe
  counts such flickers beside its verdict.
- **a-steal-after-the-guard-ends.** The guard ends 120 s after the bridge's start line, when the game exits, or at its
  bounds. A window that the game opens after that is not guarded. The measured map load took no focus (2026-11-27).
- **his-click-on-a-game-while-it-loads.** Until the guard ends, a click that he makes on the new game's window is put
  back like a steal, and so is a click on the other game that he makes with no input in the second before it (a click
  is input, so this does not happen in practice). He can bring the game forward after the guard ends, or launch with a
  front reason.
- **another-run-launching-at-the-same-time.** While a guard runs, a game window that another run's launch opens is a
  new watched window too, and is put back. A Steam start of ArchBig at the moment another run starts ArchSmall can be
  taken by Steam as ArchSmall's start (seen once, 2026-11-27: "no ArchBig process 120 s after the launch"); that is the
  launch route's, not this page's.
- **a-windows-that-refuses-the-restore.** When Windows refuses the plain call, the Alt tap and the thread attach, the
  game keeps the foreground; the guard's log line reads `"ok":false`.

## PROMISES (each one is owed a test of the same name)

- **every-start-goes-through-guarded.** In `game_instance.py` each launch act (a call that carries `STEAM_URL`, or the
  `_ps` call of a function that builds a start of `GAME_EXE`: `launch_behind.start_script` or a `Start-Process`) runs inside a `launch_behind.guarded(...)`
  argument, or in a private function reached only through one; no public function reaches a launch act outside it. No
  other file under `src/RimMandrake` starts the game itself.
- **the-guard-is-up-before-the-launch-fires.** `guarded` starts the guard and waits for its READY before it calls the
  launch, so the game's first window already meets the guard.
- **a-front-reason-starts-no-guard-and-says-why.** With a front reason, `guarded` starts no guard, calls the launch, and
  its note names the reason.
- **a-direct-start-shows-the-window-without-activating-it.** A start that this code makes itself (ArchBig's direct start,
  a named game) runs `RimWorldWin64.exe` through `RmWin.Start` with `SW_SHOWNOACTIVATE`, so its first window is shown and
  not activated; with a front reason it uses `SW_SHOWNORMAL`. Steam's own start of ArchBig is not ours to shape: there
  the guard alone acts.
- **a-guard-that-cannot-start-never-stops-the-launch.** When the guard cannot start or gives no READY, the launch still
  runs, and the note says `COULD NOT START` or `no READY`.

## LIVE (tested by `focus_probe.py run --game <game>`, not by the selftest)

- The window that was in front before the launch is in front at each sample (about ten a second), from the launch
  command through the main menu and one map load. A foreground event of the game that is undone within 50 ms is a
  flicker, counted beside the verdict; a sample that lands inside a measured flicker is that flicker.
- No new game window sits above a window that was on screen at the start, at any sample, except inside a measured
  flicker: a show of the new window and a reading with nothing above his windows, both within 50 ms.
- The game still draws: a bridge screenshot after the map load, taken while the game is behind, has content.

Later lists beside this page: `polish.md`.
