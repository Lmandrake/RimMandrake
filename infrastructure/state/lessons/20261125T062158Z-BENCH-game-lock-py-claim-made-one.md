A game_lock.py claim made in one Bash call is held by the session's process tree, so a waitalive job (detached, its own tree) is refused by that same lock when it stops or restarts the game. Wrap the job instead: waitalive.py run -- game_lock.py run <Game> --for ... -- CMD. Also: game_instance.py stop takes --instance <Game>, not a bare name, and the exiting game holds BridgeTools DLLs for a few seconds (cp: Invalid argument), so retry the copy.
item: RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO
home: skills/rimworld-deploy
