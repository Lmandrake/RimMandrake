# Polish: the tick's game-only exit and the offline holder on a free game

- A holder run that the tick sends to game b is not an in-game driver to `driver_games` (its item is a road-back id, not
  `IN_GAME_VISIT`). Between its launch and its `bridge take`, a later tick could pick the same game for another run;
  after the take, the bridge reading refuses it. No case seen yet. (2026-11-20)
- `running_now.py` shows one GAME tile, for game a; it says "jobs waiting with the game down cannot run" while game b
  can run them. (2026-11-20)
