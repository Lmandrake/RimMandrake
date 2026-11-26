A seat set in WSL (RIMFLOW_SEAT) does not reach the wsl.exe children of a Windows python.exe unless WSLENV names it, and game_instance.stop's gate (rimflow bridge idle) then refuses as seatless. game_lock.py run now passes RIMFLOW_SEAT and RM_HOST_GUARD_GAME through WSLENV; a python.exe tool that shells to WSL itself should build its child env with modcheck runner.seat_env.
item: RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS
home: skills/rimbridge (python.exe and WSL env crossing)
