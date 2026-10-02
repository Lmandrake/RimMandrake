import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for i in range(60):
    time.sleep(3)
    try:
        with RimBridge(host, port, token) as rb:
            info = rb.call("rimworld/get_game_info", {})
            status = info.get("status")
            print(i, status)
            if status == "game_loaded":
                print("LOADED")
                break
    except Exception as e:
        print(i, "err", e)
