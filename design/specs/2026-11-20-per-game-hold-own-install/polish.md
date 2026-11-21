# Polish: the per-game hold and game b's own install (a record; nobody takes lines from it)

- `modset_builder.py --apply` on game b prints the restore hint `--restore-own BENCH` without `RM_GAME_INSTANCE=b`; typed in a game-a shell it reads game a's marker, not b's (2026-11-20 live proof).
- `modset_builder.py` on game b prints "down from 315", the count of his full list, not of game b's own list (17); the number is a label only.
