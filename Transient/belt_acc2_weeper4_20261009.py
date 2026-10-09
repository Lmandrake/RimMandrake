import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
for d in ("Filth_Slime", "Filth_Ash", "Filth_Blood", "Filth_Trash", "Filth_Sand"):
    for t, x in (("Soil", 50), ("TileGranite", 52)):
        S.call("jawa/set_terrain_batch", ops="%s:%d,58" % (t, x))
        r = S.call("jawa/spawn_batch", ops="%s:%d,58" % (d, x))
        print(d, t, r.get("spawned"))
