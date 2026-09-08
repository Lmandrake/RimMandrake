import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    for m in ("rimbridge/get_bridge_status", "rimworld/get_game_info"):
        try:
            print(m, "->", json.dumps(rb.call(m))[:900])
        except Exception as e:
            print(m, "!!", type(e).__name__, str(e)[:300])
