import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
def piin():
    return [p for p in census()["pawns"] if p["kindDef"]=="RM_Piinnok" and not p["dead"]]
def hidset(ps):
    s=set()
    for p in ps:
        g=call("jawa/pawn_get", pawn=p["id"])["pawns"]
        if g and any(x["def"]=="RM_WatcherHidden" for x in g[0]["hediffs"]): s.add(p["id"])
    return s
ps=piin(); H=hidset(ps); hp=[p for p in ps if p["id"] in H]
print("hidden", len(hp), [(p["id"],p["x"],p["z"]) for p in hp])
# pick three mutually well separated hidden ones
chosen=[]
for p in hp:
    if all(abs(p["x"]-q["x"])+abs(p["z"]-q["z"])>=5 for q in chosen): chosen.append(p)
    if len(chosen)==3: break
print("chosen", [(p["id"],p["x"],p["z"]) for p in chosen])
if len(chosen)<3: raise SystemExit("not enough separated")
a,b,c=chosen
call("jawa/explosion_at", at="%d,%d"%(a["x"],a["z"]), radius=1.5, damType="Bomb", damAmount=30)
call("jawa/map_fire", action="start", rect="%d,%d,1,1"%(b["x"],b["z"]), fireSize=1.0)
r=call("jawa/damage", damageDef="AcidBurn", amount=10, x=c["x"], z=c["z"], allowColonists=True); show(r,200)
step(240)
alive={p["id"] for p in piin()}
for nm,p in zip(("explosion","fire","acid"),chosen):
    print(nm, p["id"], "DEAD" if p["id"] not in alive else "alive")
signs=call("jawa/list_things", defName="RM_WatcherSign_SandDimple")["things"]
print("signs left", len(signs), "hidden left", len(hidset(piin())), "remains", call("jawa/list_things", defName="RM_WatcherRemains_Piinnok").get("countMatched"))
