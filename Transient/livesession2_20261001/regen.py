"""Set current tile to a biome/temp, regenerate the map, plant 3 colonists. usage: regen.py BIOME TEMP"""
import sys, json, time
from bx import call
biome, temp = sys.argv[1], float(sys.argv[2])
mi = call("jawa/map_info", {}, 30); tile = mi["tile"]
r = call("jawa/world_tile_set", {"tiles": str(tile), "biome": biome, "temperature": temp}, 60)
print("tile_set", r.get("success"), str(r.get("tiles"))[:200])
call("jawa/world_commit", {}, 120)
try:
    r = call("rimworld/execute_debug_action", {"path": "Actions\\Regenerate Current Map"}, 240)
    print("regen", r.get("success"), r.get("message"))
except Exception as e:
    print("regen call ended:", e)
for i in range(30):
    time.sleep(10)
    try:
        st = call("rimbridge/get_bridge_status", {}, 20)["state"]
        if st.get("currentMapReady"):
            break
    except Exception as e:
        pass
mi = call("jawa/map_info", {}, 30)
print("map", mi.get("tile"), mi.get("mapBiome"), mi.get("outdoorTempNow"), mi.get("latitude"), mi.get("tileInfo", {}).get("hilliness"))
cx, cz = mi["sizeX"] // 2, mi["sizeZ"] // 2
r = call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": cx, "z": cz, "faction": "player", "count": 3}, 60)
print("colonists", [p.get("id") for p in (r.get("pawns") or []) if p.get("ok")], r.get("message"))
call("rimworld/execute_debug_action", {"path": "Actions\\Destroy hostile pawns"}, 60)
print("ticks", call("rimworld/get_game_info", {}, 30).get("ticksGame"))
