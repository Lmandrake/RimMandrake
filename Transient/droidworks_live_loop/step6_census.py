import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimbridge/get_bridge_status", {})
    print("status:", r.get("version"), r.get("gameLoaded") if "gameLoaded" in r else "")
    r2 = rb.call("rimworld/get_game_info", {})
    print("game_info:", r2.get("status"))
