"""setmap.py MAPID -- make MAPID current, print map_info."""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h_, p_, t_ = resolve_endpoint()
with RimBridge(h_, p_, t_) as B:
    B.call("jawa/set_current_map", {"mapId": int(sys.argv[1])}); time.sleep(0.8)
    mi = B.call("jawa/map_info", {}) or {}
    print(json.dumps({k: mi.get(k) for k in ("mapId", "sizeX", "sizeZ", "ticksGame")}))
    print(json.dumps(B.call("rimworld/get_game_info", {}), default=str)[:300])
