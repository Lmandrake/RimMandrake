import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=500): return json.dumps(x,default=str)[:n]
X,Z=100,60
print("terrain", j(S.call("jawa/set_terrain_batch", ops="WaterDeep:%d,%d,9,9"%(X-4,Z-4)),200))
r=S.call("jawa/spawn_pawn", kindDef="RSW_RimMandrakeJawa_Kind", x=X+6, z=Z, faction="player", count=1)
pid=(r.get("pawns") or [{}])[0].get("id"); print("spawn", r.get("success"), pid, j(r.get("message"),200))
print("gear", j(S.call("jawa/pawn_gear", pawn=pid, action="equip", **{"def":"guy762_JawaHood"}),300))
print("job", j(S.call("jawa/ordered_job", pawnId=pid, jobDef="GoSwimming", targetAX=X, targetAZ=Z, waitTicks=60),400))
for i in range(6):
    S.run(150)
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    r=S.call("jawa/static_call", type="RimMandrake.StarWars.JawaRules.JawaHoodProof", method="ProofHood", args="x")
    print("t",i, p.get("position"), r.get("result") if r.get("success") else j(r,300))
