import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid); S.quiet()
WR = "RimMandrake.Utinni.WasteRun.WasteRunProof"
def sc(m, a="-"):
    r = S.call("jawa/static_call", type=WR, method=m, args=a)
    return r.get("result") or r.get("message")
q = S.call("jawa/quest_lifecycle", action="accept", questId=0); print("accept", q.get("success"), str(q.get("message"))[:200])
print("gizmo A1", sc("ProofGizmo"))
print("press", sc("ProofPress", "DropOnEmpire"))
print("gizmo after", sc("ProofGizmo"))
q = S.call("jawa/quest_lifecycle", action="list"); print([(x["id"], x["name"], x["state"]) for x in q.get("quests", [])])
hl = S.call("jawa/drain_log", limit=60, contains="WasteRun"); print([m.get("text", "")[:160] for m in hl.get("messages", [])][-5:])
