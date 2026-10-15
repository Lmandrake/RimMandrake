"""r7: main menu -> fresh quicktest, then WAIT for Playing + map_info (proof_all.p1_fresh_map's loop). edge_probe 'fresh'
returned before the map finished and river_site's map generation ran concurrently (GenStep 'Collection was modified')."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    rb.call("rimworld/go_to_main_menu", {})
    r = rb.call("rimworld/start_debug_game_ready", {"readiness": "mapData", "pauseIfNeeded": True, "timeoutMs": 280000})
    st = None
    for _ in range(480):
        st = rb.call("rimworld/get_ui_state", {}).get("programState")
        if st == "Playing" and rb.call("jawa/map_info", {}).get("success"):
            break
        time.sleep(0.5)
    print("start", r.get("success"), "state", st, "map", json.dumps({k: rb.call("jawa/map_info", {}).get(k) for k in ("tile", "mapId", "sizeX")}))
