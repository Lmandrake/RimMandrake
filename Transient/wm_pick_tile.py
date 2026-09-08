import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("mapCount BEFORE:", gi.get("mapCount"), "ticks:", gi.get("ticksGame"))
    r = rb.call("jawa/tile_settleable", {"examplesPerReason": 3})
    s = json.dumps(r)
    print("settleable sweep:", s[:900])
