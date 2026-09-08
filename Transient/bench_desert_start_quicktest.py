import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("game_info before:", {k: info.get(k) for k in ("status","ticksGame","mapCount")})
    res = rb.call("rimworld/start_debug_game_ready", {})
    print("start_debug_game_ready success:", res.get("success"), res.get("start", {}).get("mapSize"))
