"""Retile the current quicktest tile to a biome and regenerate its map (recipe from CreatureBehaviors/validation.py _regen).
python.exe Transient/acc_biomes/retile.py RM_Wasteland [temperature]"""
import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
biome = sys.argv[1]; temp = float(sys.argv[2]) if len(sys.argv) > 2 else 15.0
host, port, token = rbc.resolve_endpoint()
def C(rb, t, a=None):
    try: return rb.call(t, a or {}, check=False)
    except Exception as e: return {"exc": str(e)[:200]}
with rbc.RimBridge(host, port, token, timeout=60.0) as rb:
    mi = C(rb, "jawa/map_info"); tile = mi.get("tile"); print("before", mi.get("mapBiome"), "tile", tile)
    print(json.dumps(C(rb, "jawa/world_tile_set", {"tiles": str(tile), "biome": biome, "temperature": temp}))[:200])
    print(json.dumps(C(rb, "jawa/world_commit"))[:120])
    print(json.dumps(C(rb, "rimworld/execute_debug_action", {"path": "Actions\\Regenerate Current Map"}))[:200])
for i in range(60):
    time.sleep(5)
    try:
        with rbc.RimBridge(host, port, token, timeout=30.0) as rb:
            st = (C(rb, "rimbridge/get_bridge_status").get("state") or {})
            if st.get("automationReady") and st.get("currentMapId") and not st.get("longEventPending"):
                mi = C(rb, "jawa/map_info"); print("after", mi.get("mapBiome"), "wait", i * 5); break
    except Exception as e:
        continue
else:
    print("map not ready in 300s")
