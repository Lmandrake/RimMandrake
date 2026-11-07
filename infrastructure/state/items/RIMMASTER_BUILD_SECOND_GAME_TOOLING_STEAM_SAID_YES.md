# RIMMASTER_BUILD_SECOND_GAME_TOOLING_STEAM_SAID_YES

## spec

Rung one of `design/RimMandrake/two_rimworld_instances_2026-11-07.md` passed on SteveDesktop on 2026-11-07: two games run at once with Steam's connection intact. The tools still assume one game, so a loop beside a second game is unsafe. Build that doc's list "First, to run one loop on B safely beside a loop on A", in its order: `game_instance.py` and stop-by-pid come first, since kill-by-name is what can take someone else's game.

Carry the trial's recipe fixes into the helper: B's `Prefs.xml` needs a window size, the token is written with `[IO.File]::WriteAllText` or from WSL, and Prefs are seeded without `rw_game.sh init` while A is up.

Done when: with game B up on SteveDesktop, each changed tool acts only on its own instance, shown by a selftest for each and one live round; default instance `a` behaves as it does today with no environment set.

Opening the lane is the Conductor's decision.

Source: `LIVELANE_PROBE_SECOND_GAME_INSTANCE`; readings at `D:\ClaudeWork\rimmandrake\instances_trial\readings.md` on Archmagi.
