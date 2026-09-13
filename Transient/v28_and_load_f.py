import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    s = rb.call("rimworld/save_game", {"saveName": "WORLDMAP_V28_punchlist_2026-09-09"})
    print("V28:", s.get("saveName"), s.get("sizeBytes"), flush=True)
    time.sleep(4)
    r = rb.call("rimworld/load_game", {"saveName": "gravship_f_consolidated_names_2026-09-09"})
    print("load queued:", r.get("status"), flush=True)
# poll on fresh connections; distinguish by colony presence (gravship_f has colonists)
time.sleep(15)
for i in range(30):
    try:
        with RimBridge(host, port, token) as rb:
            gi = rb.call("rimworld/get_game_info", {})
            t = gi.get("ticksGame")
            if t and t > 100000:   # gravship_f is an old colony, high ticks; worldmap saves ~1200
                print(f"gravship_f LOADED (ticks {t})", flush=True)
                break
            print(f"poll {i}: ticks {t}", flush=True)
    except Exception as e:
        print(f"poll {i}: {str(e)[:60]}", flush=True)
    time.sleep(8)
