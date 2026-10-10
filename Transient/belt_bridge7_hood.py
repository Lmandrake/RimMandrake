import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x, n=500): return json.dumps(x, default=str)[:n]
# JAWA_SWIM_HOOD_KEEP_1 A1 reread after the ReGrowthCore fix (04916d360): re-order GoSwimming each round, read after a few ticks.
pid = sys.argv[1]; X, Z = int(sys.argv[2]), int(sys.argv[3])
for i in range(8):
    o = S.call("jawa/ordered_job", pawnId=pid, jobDef="GoSwimming", targetAX=X, targetAZ=Z, waitTicks=5)
    S.call("rimworld/step_game_ticks", ticks=40)
    p = (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
    r = S.call("jawa/static_call", type="RimMandrake.StarWars.JawaRules.JawaHoodProof", method="ProofHood", args="x")
    print("t", i, o.get("afterJobDef"), p.get("position"), p.get("curJob") or p.get("job"), r.get("result") if r.get("success") else j(r, 300))
