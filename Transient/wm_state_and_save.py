import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO:", json.dumps(gi)[:400]); print()
    try:
        print("TILE 16869:", json.dumps(rb.call("jawa/world_tile_get", {"tiles":"16869"}))[:400]); print()
    except Exception as e:
        print("world_tile_get !!", type(e).__name__, str(e)[:200]); print()
