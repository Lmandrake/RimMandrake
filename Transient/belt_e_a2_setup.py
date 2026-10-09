import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
print(call("rimworld/get_game_info").get("status"))
if call("rimworld/get_game_info").get("status")!="game_loaded":
    r=call("rimworld/start_debug_game_ready",timeoutMs=280000,readiness="mapData",pauseIfNeeded=True); print(str(r)[:200])
    for _ in range(120):
        if call("rimworld/get_ui_state").get("programState")=="Playing": break
        time.sleep(1)
print(call("rimworld/get_game_info"))
