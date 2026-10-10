import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=400): return json.dumps(x,default=str)[:n]
print("end", j(S.call("jawa/game_condition", action="end", condition="Flashstorm"),200))
S.run(5)
w=S.call("jawa/weather_get"); print("conds", w.get("conditions"))
print("temp", j(S.call("jawa/cell_temperature", x=100, z=60),300))
pid=sys.argv[1]
print("job", j(S.call("jawa/ordered_job", pawnId=pid, jobDef="GoSwimming", targetAX=100, targetAZ=60, waitTicks=30),300))
for i in range(6):
    S.run(120)
    p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    r=S.call("jawa/static_call", type="RimMandrake.StarWars.JawaRules.JawaHoodProof", method="ProofHood", args="x")
    print("t",i, p.get("position"), r.get("result") if r.get("success") else j(r,300))
