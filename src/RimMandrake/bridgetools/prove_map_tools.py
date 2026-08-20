"""M1 proof: five terrain layers, substructure, map_commit."""
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
print("state:", st.get("programState"))

info = call("rimworld/get_game_info")
print("map size:", info.get("mapSize") or info.get("map") or "?")

RECT = "60,60,10,10"
print("\n== 1. FIVE LAYERS before ==")
b = call("jawa/get_terrain_layers", rect=RECT, limit=3)
print("   odyssey:", b.get("odysseyActive"), " foundationCells:", b.get("foundationCells"),
      " substructureCells:", b.get("substructureCells"))
for c in b.get("cells", []): print("   ", c)

print("\n== 2. LAY SUBSTRUCTURE over the rect ==")
s1 = call("jawa/set_substructure_batch", action="set", rect=RECT)
print("   changed:", s1.get("changed"), "of", s1.get("cellsInRect"), " refused:", s1.get("refusedCount"))
for x in (s1.get("refused") or [])[:3]: print("    refused:", x)
for c in (s1.get("cells") or [])[:3]: print("   ", c)

print("\n== 3. READ BACK via the layer reader ==")
a = call("jawa/get_terrain_layers", rect=RECT, limit=3)
print("   foundationCells:", a.get("foundationCells"), " substructureCells:", a.get("substructureCells"))
for c in a.get("cells", []): print("   ", c)

print("\n== 4. MAP COMMIT ==")
mc = call("jawa/map_commit")
print("   success:", mc.get("success"), "failed:", mc.get("failedSteps"))
for x in mc.get("steps", []): print("    ", x.get("step"), "->", x.get("status"), x.get("error",""))

print("\n== 5. UNDER-TERRAIN layer, which set_terrain cannot reach ==")
u = call("jawa/set_terrain_layer", layer="under", rect="75,60,4,4", **{"def": "Sand"})
print("   changed:", u.get("changed"), " refused:", u.get("refusedCount"))
for c in (u.get("cells") or [])[:3]: print("   ", c)

print("\n== 6. REMOVE substructure again ==")
s2 = call("jawa/set_substructure_batch", action="remove", rect=RECT)
print("   changed:", s2.get("changed"), " refused:", s2.get("refusedCount"))
f = call("jawa/get_terrain_layers", rect=RECT, limit=2)
print("   substructureCells now:", f.get("substructureCells"))
