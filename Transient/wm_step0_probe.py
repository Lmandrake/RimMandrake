import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    for m, a in (("rimbridge/get_bridge_status", {}),
                 ("rimworld/get_game_info", {}),
                 ("jawa/world_info_get", {})):
        try:
            print(m, "->", json.dumps(rb.call(m, a))[:800]); print()
        except Exception as e:
            print(m, "!!", type(e).__name__, str(e)[:400]); print()
