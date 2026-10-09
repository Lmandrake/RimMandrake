import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
r = S.call("jawa/spawn_batch", ops="RM_VenomPool:50,50;Filth_Dirt:52,50;Filth_Slime:54,50")
print(r.get("success"), str(r.get("message"))[:200])
for d in ("RM_VenomPool", "Filth_Dirt", "Filth_Slime"):
    l = S.call("jawa/list_things", defName=d, rect="40,40,30,30", limit=10)
    print(d, l.get("countMatched"))
tm = S.call("jawa/harmony_patches", typeName="FilthMaker", methodName="TryMakeFilth")
print(json.dumps(tm, default=str)[:900])
t = S.call("jawa/get_terrain_batch", rects="50,50,1,1"); print(t.get("ops"))
