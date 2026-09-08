import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
deadline = time.time() + 1500
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            ui = rb.call("rimworld/get_ui_state", {})
            ps = ui.get("programState")
            if ps == "Playing":
                gi = rb.call("rimworld/get_game_info", {})
                print("PLAYING; ticksGame:", gi.get("ticksGame"), "mapCount:", gi.get("mapCount"))
                t1 = gi.get("ticksGame")
                sys.exit(0)
            print("state:", ps, flush=True)
    except Exception as e:
        print("poll err:", e, flush=True)
    time.sleep(15)
print("TIMEOUT: never reached Playing")
sys.exit(1)
