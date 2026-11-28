# RIMMANDRAKE_LAUNCH_GAME_BEHIND_HIS_WINDOWS_IT_STEALS_FOCUS

## spec

The owner, 2026-11-27 about 9:55 PM PST: "When you launch Rimworld for testing, can you launch it not as the most
foreground window? It's very distracting to have it steal focus and be in front all the time."

Every launch path of a game on Archmagi (`game_instance.py launch`, `fire_a`, `launch_ready.py`, `live_session.py`)
starts the game through one shared function in `game_instance.py`. That function keeps the window that was the
foreground window before the launch as the foreground window, and keeps the game's window below the windows that were
open before the launch, from the launch command until the first main menu. The game still runs and draws
(runInBackground). A tool brings the game to the front only with an explicit flag for a named reason.

## verify

- Live: `src/RimMandrake/Utils/focus_probe.py` samples the foreground window and the z-order of each RimWorld window
  about ten times a second across one real launch (launch command to main menu, then one map load). Red on the parent
  commit (the game takes the foreground at least once), green after the fix, on ArchSmall, then on ArchBig.
- Offline: `src/RimMandrake/Utils/selftest_launch_behind.py` proves that each launch path calls the shared function; a
  planted path that skips the function turns it red.

## criteria

- The probe reads the game in the foreground at least once on the parent, and never after the fix, on ArchSmall.
- The same on ArchBig, or that reading recorded UNRUN with its command.
- The selftest passes, and goes red on a planted launch path that skips the shared function.

## refs

file: src/RimMandrake/Utils/game_instance.py
new: src/RimMandrake/Utils/focus_probe.py
new: src/RimMandrake/Utils/selftest_launch_behind.py
new: src/RimMandrake/Utils/launch_behind.py
new: design/specs/2026-11-27-launch-behind/boundary.md
