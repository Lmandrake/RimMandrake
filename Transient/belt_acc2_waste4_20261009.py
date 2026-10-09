import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid); S.quiet()
WR = "RimMandrake.Utinni.WasteRun.WasteRunProof"
def sc(m, a="-"):
    r = S.call("jawa/static_call", type=WR, method=m, args=a)
    return r.get("result") or r.get("message")
for dest in ("FreezeColdSide", "EntombAssailants", "IgnitePropaneLake", "SlimeExperiment"):
    S.call("jawa/spawn_batch", ops="Wastepack:50,50")
    fi = S.call("jawa/fire_incident", incidentDef="RUT_WasteRunOffer"); 
    qs = S.call("jawa/quest_lifecycle", action="list").get("quests", [])
    cur = [x for x in qs if x["state"] == "NotYetAccepted"]
    if not cur: print(dest, "no quest offered", fi.get("success"), str(fi.get("message"))[:100]); continue
    S.call("jawa/quest_lifecycle", action="accept", questId=cur[-1]["id"])
    print(dest, sc("ProofPress", dest), flush=True)
