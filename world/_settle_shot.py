import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
time.sleep(50)
for _ in range(10):
    try:
        with RimBridge(host, port, token) as rb:
            ui=rb.call("rimworld/get_ui_state", {})
            wins=[w.get("type","") for w in ui.get("windows",[])]
            loading = any("Init" in w or "Loading" in w for w in wins)
            print("state", ui.get("programState"), "loading-window:", loading, "wins:", wins[:4])
            if ui.get("programState")=="Playing" and not loading:
                rb.call("jawa/clear_ui", {}); rb.call("rimworld/close_window", {"windowType":"LudeonTK.EditWindow_Log"})
                rb.call("jawa/world_view", {"centerTile": 0, "altitude": 800})
                time.sleep(2)
                s=rb.call("rimworld/take_screenshot", {}); print("orbit shot:", s.get("path")); sys.exit(0)
    except Exception as e: print("poll", str(e)[:50])
    time.sleep(12)
print("still not settled")
