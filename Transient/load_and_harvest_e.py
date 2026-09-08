import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SAVE = "WORLDMAP_V1_original_e"
OUT = r"D:\Luke\dev\Rimworld\Transient\base_e"
import os
os.makedirs(OUT, exist_ok=True)

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/load_game", {"saveName": SAVE})
    print("load ->", json.dumps({k: v for k, v in r.items() if k != "operation"})[:220], flush=True)

t0 = time.time()
ok = False
while time.time() - t0 < 1200:
    time.sleep(20)
    try:
        with RimBridge(host, port, token) as rb:
            ui = rb.call("rimworld/get_ui_state", {})
            if ui.get("hasCurrentGame"):
                wi = rb.call("jawa/world_info_get", {})
                if wi.get("success"):
                    print("%4.0fs world up: %s" % (time.time() - t0, wi["info"]["name"]), flush=True)
                    ok = True
                    break
            print("%4.0fs %s hasGame=%s" % (time.time() - t0, ui.get("programState"), ui.get("hasCurrentGame")), flush=True)
    except Exception as e:
        print("%4.0fs poll: %s" % (time.time() - t0, str(e)[:90]), flush=True)

if not ok:
    print("DID NOT COME UP")
    sys.exit(1)

# settle before reading (the bridge answers before the game is reactive)
time.sleep(40)

with RimBridge(host, port, token) as rb:
    e = rb.call("jawa/world_tile_export", {"path": OUT + r"\tiles.csv"})
    print("tiles ->", e.get("tilesTotal"), e.get("path"), flush=True)

    lk = rb.call("jawa/world_links_get", {"range": "0-21871", "limit": 22000})
    rows = lk.get("tiles") or lk.get("rows") or []
    json.dump(rows, open(OUT + r"\links.json", "w"))
    print("links rows ->", len(rows), flush=True)

    mu = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
    mrows = mu.get("tiles") or mu.get("rows") or []
    json.dump({x["tile"]: sorted(d["def"] for d in x["mutators"]) for x in mrows},
              open(OUT + r"\mutators.json", "w"))
    print("mutator rows ->", len(mrows), flush=True)

    ob = rb.call("jawa/world_objects_get", {"limit": 5000})
    json.dump(ob.get("objects") or ob.get("rows") or [], open(OUT + r"\objects.json", "w"))
    lm = rb.call("jawa/world_landmarks_get", {"limit": 5000})
    json.dump(lm.get("landmarks") or lm.get("rows") or [], open(OUT + r"\landmarks.json", "w"))
    st = rb.call("jawa/world_stats", {})
    print("stats ->", st.get("message"), flush=True)
    json.dump({k: v for k, v in st.items() if k != "operation"}, open(OUT + r"\stats.json", "w"))
    wi = rb.call("jawa/world_info_get", {})
    json.dump(wi.get("info"), open(OUT + r"\info.json", "w"))
print("HARVEST COMPLETE ->", OUT, flush=True)
