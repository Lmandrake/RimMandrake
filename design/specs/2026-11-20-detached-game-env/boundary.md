# BOUNDARY: a detached run's unit carries the whole environment of the game it names, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/detached_helper.py` (`game_env`, used by `launch_argv`).
Item: `RIMMANDRAKE_CARRY_WSLENV_INTO_B_RUNS_PROOF_HIT_A`, written 2026-11-20. The Dispatch step
launched a game-b visit with `RM_GAME_INSTANCE=b` and an empty WSLENV. python.exe (every bridge call) did not see the
name, the bridge client fell back to game a's port 5174, and the visit's proof loaded its site onto game a while another
run held game a's bridge. Each promise has a test of its name in `src/RimMandrake/rimflow/selftest_detached_game_env.py`.

## ACCEPTS (the only inputs this is built for)

- **a-run-env.** The `env` of a run record: RM_ variables only (`--env` refuses any other key).
- **a-game-name.** `RM_GAME_INSTANCE` in that env: empty, `a`, or a name `game_instance.check_name` accepts.

## DOES NOT SURVIVE (not promised)

- **a-shell-outside-a-unit.** A command an agent runs in its own shell with its own `export RM_GAME_INSTANCE=b` gets no
  WSLENV from this code. That shell must use `game_instance.env("b")` or `WSLENV=RM_GAME_INSTANCE` (bare: `/u` did not
  reach python.exe, measured on Archmagi 2026-11-20).
- **a-moved-port.** The port and token are read when the unit is made; a game b relaunched on another port later is not
  followed.

## PROMISES (each one is owed a test of the same name)

- **a-game-b-unit-carries-its-whole-environment.** A run whose env names game b gets, as `--setenv` pairs of its unit,
  every variable `game_instance.env("b")` returns: `GABP_SERVER_PORT` 5175, `GABP_TOKEN`, `RM_GAME_LOGDIR`, and a
  `WSLENV` that names `RM_GAME_INSTANCE` bare and the port and token too. The run's other RM_ variables stay.
- **a-game-a-unit-gains-nothing.** A run whose env names game a, or no game, gets no `GABP_` or `RM_GAME_` variable it
  did not carry.
- **a-bad-game-name-is-refused.** A run whose env names a game `check_name` refuses raises `ValueError`; no unit argv is
  made for it.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
