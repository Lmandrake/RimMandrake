import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
old = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.drop_map(old, 114480)
mid = S.biome_map(114480, "RM_Stillsand", size=100, keeper=(5, 5))
open("Transient/belt_acc2_ls_map_id.txt", "w").write(str(mid))
S.call("jawa/site_state", storyteller="off", clearIncidentQueue=True)
S.call("jawa/clear_area", rect="40,40,24,24")
pass
r = S.call("jawa/spawn_pawn", kindDef="RM_Drazzik", x=50, z=50, faction="none", count=1)
dz = (r.get("pawns") or [{}])[0].get("id"); print("drazzik", dz, str(r.get("message"))[:80], flush=True)
h = S.call("jawa/spawn_pawn", kindDef="Colonist", x=56, z=50, faction="player", count=1); hid = (h.get("pawns") or [{}])[0].get("id")
pr = S.call("jawa/spawn_pawn", kindDef="Pirate", x=44, z=54, faction="Pirate", count=1); print("pirate", pr.get("success"), str(pr.get("message"))[:80], flush=True)
def ins(i): return json.dumps(S.call("jawa/inspect_string", thingIds=i).get("things"), default=str)[:400]
print("inspect0", ins(dz), flush=True)
for k in range(4):
    S.run(300)
    print(k, ins(dz), flush=True)
