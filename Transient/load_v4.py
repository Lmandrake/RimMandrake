import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
SAVE = "WORLDMAP_V9_tribes_dispersed_2026-09-07"

with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/load_game", {"saveName": SAVE})
    print("load_game ->", json.dumps(r)[:400], flush=True)

t0 = time.time()
while time.time() - t0 < 900:
    time.sleep(20)
    try:
        with RimBridge(host, port, token) as rb:
            ui = rb.call("rimworld/get_ui_state", {})
            ps = ui.get("programState")
            hg = ui.get("hasCurrentGame")
            print("%5.0fs  programState=%s hasCurrentGame=%s" % (time.time()-t0, ps, hg), flush=True)
            if hg:
                wi = rb.call("jawa/world_info_get", {})
                if wi.get("success"):
                    print("WORLD LOADED:", json.dumps(wi)[:600], flush=True)
                    break
    except Exception as e:
        print("%5.0fs  (poll error: %s)" % (time.time()-t0, e), flush=True)
print("done", flush=True)
