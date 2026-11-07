## spec
`RM_RUNNER_DIR='~/rm/gameb' rimflow bridge take --host stevedesktop.b` reports success and shows HELD, but it writes `/mnt/d/RimTest/data/instances/b/DRIVER_LOCK.json` on SteveDesktop. The game's own tools use `/mnt/d/ClaudeWork/rimmandrake/instances/b/DRIVER_LOCK.json`. So the take guards nothing, and `rw_game.sh` under game B's environment reads that lock as FREE while the take is held.

MEASURED 2026-11-07 13:21 PST: the remote take printed gen 1, while `host_guard.py status` with `RM_INSTANCES_ROOT` set printed `stevedesktop.b FREE` at the same moment.

Cause: `host_guard.remote_argv` runs on SteveDesktop with no `RM_INSTANCES_ROOT`. `.bashrc` sources `~/rm/runner/infrastructure/stevedesktop/testcentre_env.sh`, which is older than this code and does not set it, so `game_instance.root()` falls back to `<RM_DATA_ROOT>/instances`.

Done when: from Archmagi, a remote take, a remote status and `rw_game.sh` under game B's environment all read one lock file, shown by a selftest and one live take. Updating `~/rm/runner` alone may cure it, but that clone belongs to the test lane, so the fix should not depend on when it updates.

Nothing relies on this take today: the GSS and Graffiti loops hold no take, and `rw_game.sh` guards each `up` and `down`.
