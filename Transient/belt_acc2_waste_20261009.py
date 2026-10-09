import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "TemperateForest", size=100, keeper=(30, 30))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
WR = "RimMandrake.Utinni.WasteRun.WasteRunProof"
def sc(m, a="-"):
    r = S.call("jawa/static_call", type=WR, method=m, args=a)
    return r.get("result") or r.get("message")
for d in ("QuestScriptDef/RUT_WasteRun", "IncidentDef/RUT_WasteRunOffer", "ThingDef/RM_CaskBay", "ThingDef/Wastepack"):
    g = S.call("jawa/get_defs", defs=d, fields="defName"); print(d, g.get("success"), g.get("foundCount"), flush=True)
print("gizmo0", sc("ProofGizmo"))
S.call("jawa/clear_area", rect="48,48,6,6")
r = S.call("jawa/spawn_batch", ops="RM_CaskBay:50,50"); print("bay", r.get("spawned"), str(r.get("message"))[:100])
r = S.call("jawa/spawn_batch", ops="Wastepack:50,50"); print("waste", r.get("spawned"), str(r.get("message"))[:100])
print("gizmo1 (bay+waste, no quest)", sc("ProofGizmo"))
fi = S.call("jawa/fire_incident", incidentDef="RUT_WasteRunOffer"); print("fire", fi.get("success"), fi.get("fired"), str(fi.get("message"))[:200])
q = S.call("jawa/quest_lifecycle", action="list"); print("quests", json.dumps(q, default=str)[:800])
