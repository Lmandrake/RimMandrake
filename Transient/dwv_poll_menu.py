import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for i in range(20):
        r = rb.call("rimworld/get_game_info", {})
        print(i, r.get("status"), r.get("mapCount"))
        if r.get("status") != "game_loaded":
            break
        time.sleep(2)
