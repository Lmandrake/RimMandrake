import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
S.call("jawa/set_terrain_batch", ops="Soil:50,50;SoilRich:52,50;Gravel:54,50;Sand:56,50;TileGranite:58,50;Concrete:60,50;MarshyTerrain:62,50")
for i, t in enumerate(("Soil","SoilRich","Gravel","Sand","TileGranite","Concrete","Marsh")):
    x = 50 + 2 * i
    r = S.call("jawa/spawn_batch", ops="RM_VenomPool:%d,52" % x)
    # terrain at (x,52) unchanged; so paint (x,52)
for i, t in enumerate(("Soil","SoilRich","Gravel","Sand","TileGranite","Concrete","MarshyTerrain")):
    x = 50 + 2 * i
    S.call("jawa/set_terrain_batch", ops="%s:%d,54" % (t, x))
    r = S.call("jawa/spawn_batch", ops="RM_VenomPool:%d,54" % x)
    r2 = S.call("jawa/spawn_batch", ops="RM_ThornLitter:%d,56" % x)
    print(t, "venom", r.get("spawned"), "thorn", r2.get("spawned"), flush=True)
