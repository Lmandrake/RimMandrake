import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "RM_GelatinousSlime", size=100, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.quiet()
for d in ("HediffDef/RM_SharedBurden", "ThingDef/RM_SlimeHandRing", "PreceptDef/RUT_Ritual_JoiningWater"):
    g = S.call("jawa/get_defs", defs=d, fields="defName"); print(d, g.get("success"), g.get("foundCount"), g.get("notFound"))
l = S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100", limit=5)
rings = l.get("things") or []
print("rings", l.get("countMatched"), [(t["id"], t["x"], t["z"]) for t in rings])
dl = S.call("jawa/drain_log", limit=60, contains="Joining Water")
print("warn", [m.get("text", "")[:120] for m in dl.get("messages", [])][:3])
io = S.call("jawa/ideo_of")
print("ideo_of", json.dumps({k: v for k, v in io.items() if k not in ("operation", "state")}, default=str)[:600])
