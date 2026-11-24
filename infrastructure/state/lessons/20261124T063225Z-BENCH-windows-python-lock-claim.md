A Windows python cannot claim a game's driver lock: game_lock.claim imports rimflow/model.py, which imports fcntl. Hold the lock for a Windows script with a WSL child that lives as long as the script's pipe: game_lock.py run <game> --for <why> -- cat (scene_world.py lock_take).
item: RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY
home: skills/rimbridge/references/connect-and-claim.md
