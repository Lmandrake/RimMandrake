import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
import math
def piin():
    return [p for p in census()["pawns"] if p["kindDef"]=="RM_Piinnok" and not p["dead"]]
def hidmap(ps):
    d={}
    for p in ps:
        g=call("jawa/pawn_get", pawn=p["id"])["pawns"]
        d[p["id"]]=any(x["def"]=="RM_WatcherHidden" for x in g[0]["hediffs"]) if g else None
    return d
ps=piin(); print(len(ps), "hidden now", sum(hidmap(ps).values()))
edge=min(ps,key=lambda p:p["x"]); print("edge", edge["x"],edge["z"])
r=spawn_pawn("Colonist",edge["x"]-4,edge["z"],"player",1); c=r["pawns"][0]; print("colonist at",c["x"],c["z"])
step(20)
cc=[p for p in census()["pawns"] if p["id"]==c["id"]][0]
kill(c["id"]); 
dist={p["id"]:math.hypot(p["x"]-cc["x"],p["z"]-cc["z"]) for p in ps}
for t in (0,160,400):
    if t: step(t)
    h=hidmap(ps); hid=[i for i,v in h.items() if v]
    direct=[i for i in hid if dist[i]<=6.0]; ripple=[i for i in hid if dist[i]>6.0]
    print("t+%d hidden=%d direct(<=6 of colonist at t20)=%d ripple=%d"%(t,len(hid),len(direct),len(ripple)))
