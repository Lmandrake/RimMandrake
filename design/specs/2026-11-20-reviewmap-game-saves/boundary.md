# BOUNDARY: the review-map keeper watches the Saves folder of the game it drives, Design Version 0.1.0

Code: `src/RimMandrake/Utils/modcheck/reviewmap.py` (`SAVES`, `SIGNS`, and so `saves_stat`, `save_keeper`, `write_signs`).
Item: `RIMMANDRAKE_POINT_REVIEWMAP_AT_GAME_B_SAVES_KEEPER_BLIND`, written 2026-11-20. On game b, `save_keeper` wrote its
keeper into game b's Saves and reported `ok False, new []`: `SAVES` was hard-wired to game a's LocalLow, so the stat, the
never-overwrite guard and the sign sidecar all read or wrote game a's folders. Each promise has a test of its name in
`src/RimMandrake/Utils/modcheck/selftest_reviewmap_game_saves.py`.

## ACCEPTS (the only inputs this is built for)

- **a-named-game.** `RM_GAME_INSTANCE` empty, `a`, or a name `game_instance` accepts, as `game_paths` reads it at import.

## DOES NOT SURVIVE (not promised)

- **a-game-switched-after-import.** The folder is read once, at import; a process that changes its game later keeps the
  first one.
- **a-python-exe-without-wslenv.** A python.exe child that never saw `RM_GAME_INSTANCE` (no WSLENV) reads game a's folder,
  like every other tool (`design/specs/2026-11-20-detached-game-env/boundary.md`).

## PROMISES (each one is owed a test of the same name)

- **saves-follow-the-named-game.** With game b named, `SAVES` is `game_paths.SAVES`, game b's own `.../b/Saves`.
- **signs-sit-beside-the-games-saves.** `SIGNS` is the `JawaBenchReviewSigns` folder beside that game's Saves.
- **game-a-keeps-its-saves.** With no game named, `SAVES` is game a's, as `game_paths` says.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
