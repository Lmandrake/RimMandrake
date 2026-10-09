import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
print(call("jawa/get_defs", defs="TerrainDef/RM_RustCathedral_CrackedMetalSoil;PawnKindDef/RM_Watcher;ThingDef/RM_WatcherRemains_Watcher;ThingDef/RM_WatcherSign_SeamGlint", fields="defName").get("notFound"))
call("jawa/set_terrain_batch", ops="RM_RustCathedral_CrackedMetalSoil:90,30,15,15", terrainDef="RM_RustCathedral_CrackedMetalSoil"); call("jawa/map_commit")
r=spawn_pawn("RM_Watcher",96,36,"none",1); W=r["pawns"][0]["id"]; print(W, r["pawns"][0]["x"], r["pawns"][0]["z"], r.get("failedCount"))
json.dump({"W":W},open("Transient/belt_lc6_w1.json","w"))
def snap():
    p=[a for a in census()["pawns"] if a["id"]==W]
    g=call("jawa/pawn_get", pawn=W)["pawns"]
    ph=call("jawa/comp_read", thing=W, comp="WatcherStalk", members="phase,angle,endAfterRetract")
    ph=ph.get("members") or ph.get("fields") or ph
    hid=any(h["def"]=="RM_WatcherHidden" for h in g[0]["hediffs"]) if g else None
    sg=len(call("jawa/list_things", defName="RM_WatcherSign_SeamGlint")["things"])
    return (p[0]["job"]["def"] if p and p[0].get("job") else None, ph, hid, sg)
print(snap())
last=None
for i in range(30):
    step(20); s=snap(); k=json.dumps(s,default=str)
    if k!=last: print(i*20+20, s); last=k
