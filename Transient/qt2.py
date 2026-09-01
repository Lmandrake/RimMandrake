import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import game_focus
print("focus:", game_focus.focus_game())
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("state:", {k: gi.get(k) for k in ("mapCount","ticksGame")})
    try:
        rb.call("rimworld/start_debug_game_ready", {})
        print("quicktest returned in time")
    except Exception as e:
        print("quicktest timed out (expected):", str(e)[:60])
for attempt in range(20):
    time.sleep(15)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            if r.get("success") and r.get("pawns") is not None:
                print("MAP READY ~%ds, pawns %d" % ((attempt+1)*15, len(r["pawns"])))
                mi = rb.call("jawa/map_info", {})
                print("map:", mi.get("sizeX"), "x", mi.get("sizeZ"), "|", str(mi.get("tileInfo",{}).get("biome")))
                break
    except Exception as e:
        pass
