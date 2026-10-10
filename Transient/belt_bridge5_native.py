import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def j(x,n=300): return json.dumps(x,default=str)[:n]
print("weather", j(S.call("jawa/weather_set", weather="RUT_ScaldSteam", lockWeather=True),200))
X,Z=150,60
w=S.call("jawa/spawn_pawn", kindDef="RM_ScaldWalker", x=X, z=Z, faction="none", count=2); wid=[p["id"] for p in w.get("pawns") or []]
m=S.call("jawa/spawn_pawn", kindDef="Muffalo", x=X, z=Z+2, faction="none", count=2); mid=[p["id"] for p in m.get("pawns") or []]
print("walkers", wid, j(w.get("message"),100), "controls", mid)
print("devil", j(S.call("jawa/spawn_batch", ops="RM_SteamDevil:%d,%d"%(X+1,Z+1)),250))
def hed(pid):
    q=S.call("jawa/pawn_get", pawn=pid).get("pawns") or []
    if not q: return "GONE"
    return [(h.get("def"),round(h.get("severity") or 0,2)) for h in q[0].get("hediffs") or []], q[0].get("position")
for i in range(8):
    S.run(150)
    dv=S.call("jawa/list_things", defName="RM_SteamDevil", limit=5).get("things") or []
    print("t+%d devil"%((i+1)*150), [(d.get("x"),d.get("z")) for d in dv], "| walkers", [hed(p) for p in wid], "| muffalo", [hed(p) for p in mid])
