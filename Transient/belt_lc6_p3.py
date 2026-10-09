import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
def piin():
    r=census(); return [p for p in r["pawns"] if p["kindDef"]=="RM_Piinnok"]
def hid(ids):
    n=0;h={}
    for i in ids:
        g=call("jawa/pawn_get", pawn=i)["pawns"]
        h[i]=any(x["def"]=="RM_WatcherHidden" for x in g[0]["hediffs"]) if g else None
    return h
# clear nearby animals first
r=census()
for p in r["pawns"]:
    if not p["isColonist"] and p["kindDef"]!="RM_Piinnok" and abs(p["x"]-52)<30 and abs(p["z"]-52)<30:
        kill(p["id"])
spawn_pawn("RM_Piinnok",51,51,"none",8)
step(200)
ps=piin(); ids=[p["id"] for p in ps]; print(len(ids), [(p["x"],p["z"]) for p in ps])
print("settled hidden:", sum(1 for v in hid(ids).values() if v))
for i in range(60):
    step(250); h=hid(ids); n=sum(1 for v in h.values() if v)
    if n==0: print("all emerged after ~", (i+1)*250, "ticks"); break
else: print("still hidden", n)
others=[(p["name"],p["x"],p["z"]) for p in census()["pawns"] if p["kindDef"]!="RM_Piinnok" and abs(p["x"]-50)<20 and abs(p["z"]-50)<20]
print("others near:", others)
