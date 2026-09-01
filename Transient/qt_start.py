import sys, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import game_focus
try:
    print("preflight:", game_focus.preflight())
except Exception as e:
    print("preflight ERR:", str(e)[:120])
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("state:", {k: gi.get(k) for k in ("mapCount","ticksGame")})
    try:
        rb.call("rimworld/start_debug_game_ready", {})
        print("quicktest call returned in time")
    except Exception as e:
        print("quicktest call timed out as documented:", str(e)[:80])
# fresh connection, poll for map
for attempt in range(12):
    time.sleep(15)
    try:
        with RimBridge(host, port, token) as rb:
            r = rb.call("jawa/list_pawns", {})
            if r.get("success") and r.get("pawns") is not None:
                print("MAP READY after ~%ds, pawns: %d" % ((attempt+1)*15, len(r.get("pawns", []))))
                mi = rb.call("jawa/map_info", {})
                print("map:", mi.get("sizeX"), "x", mi.get("sizeZ"), "biome:", str(mi.get("tileInfo",{}).get("biome")))
                break
    except Exception as e:
        print("poll", attempt, str(e)[:60])
