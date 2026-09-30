"""Prove the Middenshell is TWENTY cells wide and crawls (WASTELAND_MIDDENSHELL_FOOTPRINT_1).

Run under Windows python.exe from the repo root, with RimMandrake: Wasteland active:
    python.exe src\\RimMandrake\\bridgetools\\prove_middenshell.py
Needs a playing game or starts a debug quicktest. Steps:
  1. defs: RM_Middenshell (size 20x20), RM_MiddenshellArrives, RM_MiddenshellSeam.
  2. Make an RM_Wasteland map: set a free world tile's biome, generate its map, switch to it.
  3. Fire RM_MiddenshellArrives there (the real biome-gated path). If jawa/fire_incident is
     compiled out (GM tool) or refuses, fall back to spawning it directly mid-map.
  4. Read it back: list_things position/rotation + inspect_string "Footprint: WxH".
  5. Step ticks and read again: position must change (it crawls), footprint must stay 20x20.
Exit 0 = found on an RM_Wasteland map with a 20x20 footprint that moved; 1 otherwise.
State reads only, no screenshots."""
import sys, json, re, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()

def call(t, **p):
    try:
        r = S.call(t, p) or {}
    except Exception as e:  # a missing tool must read as UNMEASURED, never as absent
        return {"success": False, "error": "call failed: %r" % (e,)}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

def short(x, n=500): return json.dumps(x)[:n]

# 1. defs
for d in ("ThingDef/RM_Middenshell", "IncidentDef/RM_MiddenshellArrives", "ThingDef/RM_MiddenshellSeam"):
    r = call("jawa/get_defs", defs=d)   # STRING, never a list
    print("get_defs", d, "success=%s found=%s notFound=%s" % (r.get("success"), r.get("foundCount"), r.get("notFound")))

# 0. a game
st = call("rimworld/get_ui_state")
if st.get("programState") != "Playing":
    print("start_debug_game_ready:", short(call("rimworld/start_debug_game_ready", timeoutMs=280000,
                                                readiness="mapData", pauseIfNeeded=True), 300))
    for _ in range(120):
        st = call("rimworld/get_ui_state")
        if st.get("programState") == "Playing": break
        time.sleep(1)
print("programState:", st.get("programState"))

# 2. an RM_Wasteland map
home = call("jawa/map_info")
home_tile = home.get("tile")
print("home map_info:", short(home, 300))
# Any tile other than home: world_tile_set makes it flat dry land carrying our biome, so
# whether it neighbours home does not matter.
tile = None if home_tile is None else home_tile + 1
print("wasteland tile:", tile)
map_id = None
if tile is not None:
    print("world_tile_set:", short(call("jawa/world_tile_set", tiles=str(tile), biome="RM_Wasteland",
                                        elevation=200.0, hilliness="Flat", readBack=1), 300))
    call("jawa/world_commit")
    g = call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Settlement", sizeX=150, sizeZ=150)
    print("world_tile_map_generate:", short(g, 400))
    map_id = g.get("mapId")   # Map.uniqueID, what set_current_map takes
    if map_id is not None:
        print("set_current_map:", short(call("jawa/set_current_map", mapId=map_id), 200))
info = call("jawa/map_info")
biome = info.get("mapBiome")
print("current map biome:", biome, "mapId:", info.get("mapId"), "size:", info.get("sizeX"), info.get("sizeZ"))

# 3. the real path, then the fallback
fire = call("jawa/fire_incident", incidentDef="RM_MiddenshellArrives")
print("fire_incident:", short(fire, 400))
found = call("jawa/list_things", defName="RM_Middenshell", limit=5)
things = found.get("things") or found.get("results") or []
route = "incident"
if not things:
    route = "direct spawn (incident did not place one: see above)"
    print("spawn_thing:", short(call("rimworld/spawn_thing", ops="RM_Middenshell:75,75"), 300))
    found = call("jawa/list_things", defName="RM_Middenshell", limit=5)
    things = found.get("things") or found.get("results") or []
print("route:", route, "| list_things:", short(found, 400))

def read():
    f = call("jawa/list_things", defName="RM_Middenshell", limit=5)
    th = (f.get("things") or f.get("results") or [])
    ins = call("jawa/inspect_string", defName="RM_Middenshell", limit=1)
    txt = json.dumps(ins)
    m = re.search(r"Footprint: (\d+)x(\d+)", txt)
    return (th[0] if th else None), (tuple(map(int, m.groups())) if m else None), txt

t1, fp1, txt1 = read()
print("read 1:", short(t1, 300), "footprint:", fp1)
call("rimworld/step_game_ticks", ticks=2500)
t2, fp2, txt2 = read()
print("read 2:", short(t2, 300), "footprint:", fp2)
print("inspect:", txt2[:600])
logs = call("jawa/drain_log", errorsOnly=True)
print("errors:", short(logs, 1500))

moved = bool(t1 and t2 and t1.get("position") != t2.get("position"))
ok = biome == "RM_Wasteland" and fp1 == (20, 20) and fp2 == (20, 20) and moved
print("VERDICT biome=%s footprint=%s->%s moved=%s route=%s => %s"
      % (biome, fp1, fp2, moved, route, "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
