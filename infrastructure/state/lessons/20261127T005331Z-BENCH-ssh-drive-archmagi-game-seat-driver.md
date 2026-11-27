To drive an Archmagi game from another machine over ssh, run one script there that exports RM_DRIVER_PID=$$ and RIMFLOW_SEAT=<seat>, claims each game with game_lock.py claim, and releases on EXIT. Without the seat, game_instance.py stop is refused (rimflow bridge idle asks which seat). A nested 'game_lock.py run' does not make the children the holder, so their stop is refused too (2026-11-26, R3 load from SteveDesktop).
item: RIMMANDRAKE_STRIP_CORPSE_TWINS_OF_PRUNED_RACES_CHECK_SAID_NONE
home: skills/rimbridge
