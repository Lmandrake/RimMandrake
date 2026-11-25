# BOUNDARY: game watch tick

Code: `src/RimMandrake/Utils/game_watch_tick.py`, run by `src/RimMandrake/Utils/systemd/rm-game-watch.timer`.
Item: `RIMMANDRAKE_BUILD_GAME_WATCHER_NAMES_THE_BROKEN_STATE`. Tests: `src/RimMandrake/Utils/selftest_game_watch_tick.py`.
The states are named by `game_watcher.py` ([its page](../2026-11-23-bridge-v2-watcher/boundary.md)).

## ACCEPTS

`tick` looks once at each local game (ArchBig, ArchSmall) and stops one that is broken. `check` answers whether the
watcher runs: exit 0 when the last reading is fresh and each local game has been read in a named state at least once by
the tick; 1 when not; 2 when the reading cannot be read. `show` prints the last reading.

## LIMITS

- **A stop needs an episode at least 1080 s old.** The danger is a stop of a game that would recover. Measured 2026-11-24
  over the heartbeat records of both games (325 segments, 2026-11-20 to 2026-11-24): 4 silences of a main thread passed
  60 s outside a save or a long event. Two recovered (107.4 s in `update`, 61.8 s in `frame-rest`); two never did (642 s
  and 1995 s, when someone ended them). 1080 s is ten times the longest that recovered. No record shows how long a
  streak of throwing frames or a load can last and still recover, so the same age holds for both. An agent that wants
  the game sooner runs `game_instance.py stop --broken --instance <game>` at 60 s, by its own act.
- **The reading is fresh for 900 s.** The danger is a dead timer that reads alive. The timer beats each 2 minutes.

## PROMISES

- **a-broken-game-is-stopped.** Each broken state old enough is stopped through `game_instance.stop(broken=True)`, which
  confirms again, on any game, held or not. An episode younger than the limit is not stopped.
- **a-healthy-or-blind-game-is-never-stopped.** Every other state, could_not_look and process_gone included, stops
  nothing. A game that is blind while it runs keeps `blind_since` in the reading.
- **a-stop-is-reported.** A stop, a failed stop and a refused stop each write one row in `stops.jsonl`. A stop and a failed
  stop also wake the Conductor with one signal that names the game, the state and the evidence, and keep a copy of that
  game's Player.log. A report that fails is written in the row and never hides the stop.
- **one-game-never-stops-the-other.** A game whose look raises reads blind with its cause; the other game is looked at.
- **off-looks-and-does-not-stop.** `./pipe off family:game_watch` (or an unreadable switch store) lets the tick look and
  stop nothing; the reading says why.
- **check-tells-the-cases-apart.** No reading or a stale reading is 1, a reading that cannot be parsed is 2, a game that
  was never read in a named state is 1 and is named.

## DOES NOT SURVIVE

- **a-process-frozen-whole.** A suspended or crashed process writes no heartbeat, so it reads could_not_look.
- **a-hang-inside-a-save-or-a-long-event.** The watcher cannot tell it from slow work (Grey Sea, 20 minutes, recovered).
