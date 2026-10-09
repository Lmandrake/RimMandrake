import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid); S.quiet()
WR = "RimMandrake.Utinni.WasteRun.WasteRunProof"
def sc(m, a="-"):
    r = S.call("jawa/static_call", type=WR, method=m, args=a)
    return r.get("result") or r.get("message")
bay = (S.call("jawa/list_things", defName="RM_CaskBay", rect="40,40,20,20").get("things") or [{}])[0]
print("bay", bay.get("id"), bay.get("faction"))
for fac in ("PlayerColony", "Player"):
    r = S.call("jawa/set_thing_props", thing=bay["id"], faction=fac); print("set", fac, r.get("success"), str(r.get("message"))[:120])
    g = sc("ProofGizmo"); print(g)
    if "bays=1" in g: break
mi = S.call("jawa/map_info"); print("playerhome?", {k: mi.get(k) for k in mi if "home" in k.lower() or "player" in k.lower()})
