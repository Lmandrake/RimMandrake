import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
ps=[p for p in census()["pawns"] if p["kindDef"]=="RM_Piinnok" and not p["dead"]]
p=ps[0]; P=p["id"]; x,z=p["x"],p["z"]; print(P,x,z,p["job"])
call("jawa/set_terrain_batch", ops="Soil:%d,%d,1,1"%(x,z), terrainDef="Soil"); call("jawa/map_commit")
for i in range(8):
    step(40); q=[a for a in census()["pawns"] if a["id"]==P][0]
    g=call("jawa/pawn_get", pawn=P)["pawns"][0]
    print(i, q["job"], (q["x"],q["z"]), "hidden" if any(h["def"]=="RM_WatcherHidden" for h in g["hediffs"]) else "visible")
t=call("jawa/get_terrain_batch", rect="%d,%d,1,1"%(q["x"],q["z"])) if False else None
