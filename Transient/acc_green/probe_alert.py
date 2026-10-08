import sys, json
sys.path.insert(0, "Transient/acc_green")
from b import call
mi = call("jawa/map_info"); x, z = mi["sizeX"]//2, mi["sizeZ"]//2
print("map", mi["sizeX"], mi["sizeZ"])
r = call("jawa/spawn_pawn", kindDef="RM_Skivvik", x=x, z=z, faction="none", count=2); print("spawn", json.dumps(r)[:300])
def listed():
    a = call("jawa/alerts_list"); return [(q["type"], q.get("label")) for q in a.get("alerts", []) if "Vermin" in q["type"] or "Skiv" in str(q)]
for i in range(6):
    call("rimworld/step_game_ticks", ticks=120)
    print(i, listed(), call("jawa/alerts_list").get("count"))
