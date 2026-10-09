import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
def hid():
    out=[]
    for p in census()["pawns"]:
        if p["kindDef"]=="RM_Piinnok" and not p["dead"]:
            g=call("jawa/pawn_get", pawn=p["id"])["pawns"][0]
            if any(h["def"]=="RM_WatcherHidden" for h in g["hediffs"]): out.append(p["id"])
    return sorted(out)
ps=[p for p in census()["pawns"] if p["kindDef"]=="RM_Piinnok" and not p["dead"]]
a=ps[0]
r=spawn_pawn("Colonist",a["x"]+2,a["z"],"player",1); cid=r["pawns"][0]["id"]
step(240); kill(cid); step(30)
H=hid(); S=sorted((t["x"],t["z"]) for t in call("jawa/list_things", defName="RM_WatcherSign_SandDimple")["things"])
print("before save: hidden",len(H),"signs",len(S)); json.dump({"H":H,"S":S},open("Transient/belt_lc6_p8.json","w"))
show(call("rimworld/save_game", saveName="belt_lc6_watchers"),300)
