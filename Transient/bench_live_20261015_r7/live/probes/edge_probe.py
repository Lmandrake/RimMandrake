"""r7: which map edges carry moving river water on the current map (the swept row needs a DOWNSTREAM edge)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "FlowWorks", "northstar"))
from rimbridge_client import RimBridge, resolve_endpoint
import site_spec as S
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    if len(sys.argv) > 1 and sys.argv[1] == "fresh":
        rb.call("rimworld/go_to_main_menu", {})
        print("fresh", json.dumps(rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True, "timeoutMs": 280000}))[:200])
    mi = rb.call("jawa/map_info", {})
    w, hh = mi["sizeX"], mi["sizeZ"]
    tb = rb.call("jawa/get_terrain_batch", {"rects": "0,0,%d,1;0,%d,%d,1;0,0,1,%d;%d,0,1,%d" % (w, hh - 1, w, hh, w - 1, hh)})
    terr = S.parse_ops(tb.get("ops"))
    edges = {"south z=0": [(x, 0) for x in range(w)], "north z=%d" % (hh - 1): [(x, hh - 1) for x in range(w)],
             "west x=0": [(0, z) for z in range(hh)], "east x=%d" % (w - 1): [(w - 1, z) for z in range(hh)]}
    print("tile", mi.get("tile"), "mapId", mi.get("mapId"), {k: sum("Moving" in str(terr.get(c) or "") for c in v) for k, v in edges.items()})
