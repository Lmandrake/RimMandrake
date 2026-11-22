# Polish: the names of the games

- `control.py` undo lines (`pipe undo`) still print a switch's raw scope (`game:a`); `describe` and `cmd_switch` show the name.
- Code comments and docstrings across rimflow and Utils still say "game a" / "game b"; every printed line goes through `game_names`.
- `game_instance.py launch`/`stop` texts are named by `name_text` after formatting, not at each format string.
