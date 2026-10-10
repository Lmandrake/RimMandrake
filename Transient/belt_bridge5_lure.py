import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=300): return json.dumps(x,default=str)[:n]
X,Z=118,80
d=S.call("jawa/spawn_pawn", kindDef="RM_Drazzik", x=X, z=Z, faction="none", count=1); did=(d.get("pawns") or [{}])[0].get("id"); print("drazzik", did, j(d.get("message"),120))
h=S.call("jawa/spawn_pawn", kindDef="Drifter", x=X+8, z=Z, faction="hostile", count=1); hid=(h.get("pawns") or [{}])[0].get("id"); print("hostile", hid, j(h.get("message"),160))
prev=None
for i in range(10):
    r=S.call("jawa/inspect_string", thingIds=did)
    ins=[l for l in ((r.get("things") or [{}])[0].get("inspect") or []) if "decision" in l.lower()]
    print("t+%d"%(i*90), ins)
    S.run(90)
