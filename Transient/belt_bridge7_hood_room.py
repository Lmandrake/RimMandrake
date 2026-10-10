import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def j(x, n=300): return json.dumps(x, default=str)[:n]
# JAWA_SWIM_HOOD_KEEP_1 A1: the quicktest map refuses GoSwimming outdoors (FailOn NextDestIsOutdoorsAndNotEnjoyable;
# some world-scope condition blocks AllowEnjoyableOutsideNow). Enclose + roof the pool so the room is indoors.
A, B = 114, 126
ops = []
for x in range(A, B + 1):
    ops += ["Wall:%d,%d" % (x, A), "Wall:%d,%d" % (x, B)]
for z in range(A + 1, B):
    ops += ["Wall:%d,%d" % (A, z), "Wall:%d,%d" % (B, z)]
print("walls", j(S.call("jawa/build_batch", ops=";".join(ops), stuff="Steel", faction="player")))
print("roof", j(S.call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % (A + 1, A + 1, B - A - 1, B - A - 1))))
r = S.call("jawa/spawn_pawn", kindDef="RSW_RimMandrakeJawa_Kind", x=A + 1, z=A + 1, faction="player", count=1)
pid = (r.get("pawns") or [{}])[0].get("id"); print("spawn", pid)
S.call("rimworld/step_game_ticks", ticks=5)
for i in range(6):
    S.call("rimworld/set_time_speed", speed=1)
    o = S.call("jawa/ordered_job", pawnId=pid, jobDef="GoSwimming", targetAX=120, targetAZ=120, waitTicks=60)
    S.call("rimworld/set_time_speed", speed=0)
    p = (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    r = S.call("jawa/static_call", type="RimMandrake.StarWars.JawaRules.JawaHoodProof", method="ProofHood", args="x")
    print("t", i, o.get("afterJobDef"), p.get("position"), r.get("result") if r.get("success") else j(r))
print("PID", pid)
