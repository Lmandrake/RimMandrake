# BOUNDARY: wrap-up debts and relaunches

Code: `src/RimMandrake/rimflow/wrapup.py` (`owe`, debt census, standing and sweep).
Tests are in `src/RimMandrake/rimflow/selftest_wrapup_void_relaunch.py`.

## ACCEPTS

- The process's `RM_GAME_INSTANCE`, resolved to a letter by `game_instance.current()`. An unset value means `a`.
- Local debt files and filed rows. A record written before the game field was added belongs to ArchBig (`a`).

## PROMISES

- **debts-keep-the-games-letter.** Settings and scenes carry the game's letter in the register and in filed rows.
- **only-the-debts-game-can-void-it.** ArchBig and Steve1 use `Player-prev.log` in the local first game's log
  directory, with `RM_WRAPUP_PREV_LOG` as an override. Named instances use `<instances root>/<letter>/Player.log.prev`.
  When a debt predates its own previous log's last write by more than the clock-skew margin, release preflight and
  restore skip it, it stops standing, and sweep clears it. A missing or unreadable log leaves that game's debts standing.
