import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
def show(tag, r):
    print(tag, "|", json.dumps(r, default=str)[:700]); sys.stdout.flush()
for i in range(30):
    g=json.dumps(S.call("rimworld/get_game_info"),default=str)
    if '"Playing"' in g: break
    time.sleep(3)
print("state", g[:200])
try: S.quiet()
except Exception as e: print("quiet", e)
show("GOO", S.call("jawa/get_defs", defs="ThingDef/AA_GreenGoo", fields="race.deathAction"))
W="RimMandrake.Webwork.RM_WebworkProof"
d=S.call("jawa/static_call", type=W, method="ProofHarvestDesignate", args="RM_Webwork_Anchor"); show("WEBDES", d)
res=str(d.get("result",""))
if res.startswith("DESIGNATED"):
    xz=res.split()[1]
    S.run(2000)
    show("WEBREAD", S.call("jawa/static_call", type=W, method="ProofHarvestRead", args=xz))
    S.run(1500)
    show("WEBREAD2", S.call("jawa/static_call", type=W, method="ProofHarvestRead", args=xz))
with S.Scene("gloom", 40, 40, 30, 12) as sc:
    host = sc.pawn("RM_Gloomcast", 22, 6)
    fol = {k: sc.pawn(k, 2 + i*2, 6) for i, k in enumerate(["RM_Chorn", "RM_Gennok", "RM_Tebbra"])}
    for step in range(3):
        S.run(500)
        for k,p in fol.items():
            show("JOB%d %s"%(step,k), S.call("jawa/static_call", type="RimMandrake.CreatureBehaviors.RM_PawnJobProof", method="ProofJob", args=str(p)).get("result"))
