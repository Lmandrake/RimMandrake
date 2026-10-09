import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
ps = S.call("jawa/list_pawns", limit=300).get("pawns") or []
print([(p["kind"], p["x"], p["z"]) for p in ps if p["kind"] in ("RM_Mirrak", "RM_Gulloth")])
g = S.call("jawa/run_genstep", genStepDef="RM_GenStep_CleanPatches")
print(json.dumps({k: v for k, v in g.items() if k not in ("operation", "state")}, default=str)[:600])
l = S.call("jawa/list_things", defName="RM_LongShadeCleanPatch", rect="0,0,100,100", limit=20)
print(l.get("countMatched"), l.get("perDef"))
d = S.call("jawa/drain_log", limit=40, contains="LongShade")
print([m.get("text", "")[:200] for m in d.get("messages", [])][-6:])
d = S.call("jawa/drain_log", limit=40, errorsOnly=True)
print([m.get("text", "")[:160] for m in d.get("messages", [])][-4:])
