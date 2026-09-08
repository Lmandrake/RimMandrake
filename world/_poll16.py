import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for _ in range(80):
    try:
        with RimBridge(host, port, token) as rb:
            ui=rb.call("rimworld/get_ui_state", {})
            if ui.get("programState")=="Playing":
                gi=rb.call("rimworld/get_game_info", {}); print("PLAYING ticks", gi.get("ticksGame"), "maps", gi.get("mapCount")); sys.exit(0)
    except Exception as e: print("poll:", str(e)[:50])
    time.sleep(10)
print("timeout")
