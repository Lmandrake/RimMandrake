import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
cells = [(67,31),(67,34),(73,40),(73,43),(76,43),(79,31),(67,25),(20,20),(50,50),(80,80)]
for (x,z) in cells:
    r = S.call("jawa/spawn_pawn", kindDef="RM_Mirrak", x=x, z=z, faction="none", count=1)
    g = S.call("jawa/run_genstep", genStepDef="RM_GenStep_CleanPatches")
    l = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", rect="0,0,100,100", limit=20)
    print((x,z), r.get("success"), g.get("success"), l.get("countMatched"), [(t["x"],t["z"]) for t in l.get("things",[])][:3], flush=True)
