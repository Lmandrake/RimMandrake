# BOUNDARY: modcheck puts a game it holds onto its composed list, Design Version 0.1.0

Code: `src/RimMandrake/Utils/modcheck/runner.py` (`prepare_live_list`, `restart_onto_list`, `owns_game`,
`prune_uninstalled`, `deploy_mods`), with `src/RimMandrake/rimflow/game_lock.py` (`mine`, and `run`'s aim of CMD at the
game that it holds; promises on `design/specs/2026-11-21-one-game-lock/boundary.md`). Item
`RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS`. Each promise has a test of its name in
`src/RimMandrake/Utils/modcheck/selftest_restart_onto_list.py`. The live acceptance is `accept_live.py` in this folder,
fed by `live_accept.sh <game>`.

Words: the **list** is what `run()` writes to ModsConfig (MINIMAL, then the mods under test and their closure). The
**running load** is what the game loaded (`jawa/running_mods`). A game is **held** by this process when
`game_lock.py mine <game>` exits 0.

## ACCEPTS (the only inputs this is built for)

- **a-held-archmagi-game.** ArchBig or ArchSmall, named by `RM_GAME_INSTANCE` (`game_lock.py run` sets it), held through
  `game_lock.py run` (python.exe inherits the take through `RM_HOST_GUARD_GEN`).
- **a-modsconfig.** A ModsConfig with one `<activeMods>` block of `<li>` ids.
- **install-roots.** The game's Mods, the Workshop and the game's Data, as `game_paths` names them.

## DOES NOT SURVIVE (not promised)

- **a-game-on-steve-desktop.** Its worker owns its restart (`MODCHECK_STALE_KEEP_COMPOSED`); `mine` cannot see its lock.
- **a-caller-that-does-not-hold-the-game.** It gets the old path: the run reads UNMEASURED stale_load and the caller
  restarts.
- **a-changed-mod-on-the-right-list.** A game already on the list that loaded an older copy of a mod is not restarted:
  the load check reads ids, not file contents.
- **a-missing-dependency-of-the-mod-under-test.** It stays in the list and reads mod_not_installed, and one restart is
  spent before that reading.

## PROMISES (each one is owed a test of the same name)

- **prune-drops-a-base-id-no-folder-holds.** An id of `<activeMods>` that no install root holds (itself or through its
  composed mod) and that is not a DLC and not an id of the mods under test is removed, with a PRUNED line. Nothing outside
  `<activeMods>` changes. A blind install scan removes nothing.
- **restart-only-on-a-game-this-process-holds.** A game that is free, another driver's, or whose lock cannot be read is
  never stopped. The refusal names the lock's answer.
- **restart-stops-deploys-launches-in-that-order.** On a held game: stop, wait until its process is gone, deploy, then
  `launch --wait`. The record names the game, the gap that it read, and each step with its exit and words. Each wsl.exe
  child gets a seat named in WSLENV (`seat_env`), since the stop's bridge gate refuses a seatless call.
- **a-game-that-ignores-the-soft-stop-is-forced-once.** A game still up after the stop patience gets one `--force` stop.
  A game still up after that is not launched over, and the refusal says so.
- **a-refused-stop-or-launch-is-named.** A refused stop (his hold, a bridge gate) deploys and launches nothing. A failed
  launch is named with its words. A refusal after the stop says that the game is left stopped.
- **a-deploy-that-meets-held-dlls-is-tried-again.** A deploy that fails while the exiting game holds its DLLs is tried
  again. A deploy that keeps failing, or hangs past its deadline, launches nothing and names the last error; it never
  raises out with the game down.
- **prepare-restarts-only-when-the-running-load-is-not-the-list.** A held game whose running load is not the list is
  restarted (the restart deploys). A held game already on the list is deployed as before. A game that this process does
  not hold, `MODCHECK_KEEP_MODLIST` and `MODCHECK_STALE_KEEP_COMPOSED` (a caller that restarts its own game) are never
  restarted. A refused restart deploys as before. A held game whose
  running load refuses the deploy is restarted.

## LIMITS

- `STOP_PATIENCE_S = 120`: danger, a game that ignores the soft stop holds the restart with no end (seen once,
  2026-11-25). Measured need: a few seconds after taskkill.
- `DEPLOY_TRIES = 4`, `DEPLOY_RETRY_S = 10`: danger, the exiting game holds its DLLs for a few seconds and the first
  copy fails. Measured need: one retry after a few seconds.
- `_CALL_S`: hang guards of one call each (time_budget's call class, 1800 s); launch is bounded by `game_instance`
  `WAIT_S` (3600 s) plus the call class.
