A selftest that sets the script's own re-entry guard (RW_GAME_GUARDED=1) skips the guard path, so a fault there is never seen. rw_game.sh down was tested only that way. Its own RUNNER guard then made bridge idle refuse every idle stop (7 of 7 on 2026-11-26). Test a guarded script at least once the way its real caller sends it.
item: RIMMANDRAKE_UNBLOCK_IDLE_STOP_OWN_RUNNER_REFUSES_SEVEN_TIMES
home: skills/rimworld-modding/references/project-engine-facts.md
