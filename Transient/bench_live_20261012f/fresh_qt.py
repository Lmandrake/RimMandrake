import sys, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    print(rb.call("rimworld/go_to_main_menu").get("success"))
    print(rb.call("rimworld/start_debug_game_ready", {"readiness":"mapData","pauseIfNeeded":True,"timeoutMs":280000}).get("success"))
    for _ in range(120):
        if rb.call("rimworld/get_ui_state").get("programState")=="Playing": break
        time.sleep(2)
    print(rb.call("jawa/map_info"))
