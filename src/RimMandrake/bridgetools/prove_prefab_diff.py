"""M3 rigorous diff: capture a region, replay it, compare CELL CONTENTS."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
call("jawa/set_fog", action="unfogAll")

X0, Z0, W, H = 120, 120, 9, 7
ops = []
for i in range(W):
    ops.append("Wall:%d,%d" % (X0+i, Z0)); ops.append("Wall:%d,%d" % (X0+i, Z0+H-1))
for j in range(1, H-1):
    ops.append("Wall:%d,%d" % (X0, Z0+j)); ops.append("Wall:%d,%d" % (X0+W-1, Z0+j))
ops = [o for o in ops if o != "Wall:%d,%d" % (X0+4, Z0)]
ops.append("Door:%d,%d" % (X0+4, Z0))
call("jawa/build_batch", ops=";".join(ops), stuff="Steel", faction="PlayerColony")
call("jawa/build_batch", ops="Bed:122,123;StandingLamp:126,123;Table2x2c:124,122",
     stuff="WoodLog", faction="PlayerColony")
call("jawa/set_terrain_batch", ops="Concrete:%d,%d,%d,%d" % (X0+1, Z0+1, W-2, H-2))

# capture WITHOUT loose natural rock so the comparison is about what we built
cap = call("jawa/prefab_capture", name="hut2", rect="%d,%d,%d,%d" % (X0, Z0, W, H),
           copyAllThings=False, copyTerrain=True, overwrite=True)
print("capture size:", cap.get("size"), " things:", cap.get("thingCount"))
print("contents:", cap.get("contents"))

p = call("jawa/prefab_place", name="hut2", pos="160,120", faction="PlayerColony")
things = p.get("things") or []
print("placed:", p.get("spawnedCount"))

# the tool returns only readBack rows; ask the map instead for the real footprint
lt = call("jawa/list_things", **{"filter": ""}) if False else None

def terrain_map(x, z, w, h):
    r = call("jawa/get_terrain_layers", rect="%d,%d,%d,%d" % (x, z, w, h), limit=400)
    return {(c["x"]-x, c["z"]-z): c["top"] for c in (r.get("cells") or [])}

# find the copy's actual min corner by scanning for our Concrete floor near 160,120
best, bestscore = None, -1
src = terrain_map(X0, Z0, W, H)
for ox in range(150, 172):
    for oz in range(110, 132):
        cand = terrain_map(ox, oz, W, H)
        score = sum(1 for k, v in src.items() if cand.get(k) == v)
        if score > bestscore: bestscore, best = score, (ox, oz)
print("\nbest-aligned copy origin:", best, " terrain cells identical: %d of %d" % (bestscore, len(src)))
print("=> SpawnPrefab centres on pos; the min corner is pos - size/2, NOT pos.")

# now diff THINGS at that origin
def things_at(x, z, w, h):
    out = {}
    r = call("jawa/get_terrain_layers", rect="%d,%d,%d,%d" % (x, z, w, h), limit=400)
    return r
ox, oz = best
print("\nsource origin (%d,%d) vs copy origin (%d,%d)" % (X0, Z0, ox, oz))
