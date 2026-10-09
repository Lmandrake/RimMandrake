import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc3_slime_map_id.txt").read()); S.call("jawa/set_current_map", mapId=mid)
ring=(S.call("jawa/list_things", defName="RM_SlimeHandRing", rect="0,0,100,100").get("things") or [{}])[0]
for kw in (dict(ritual="RUT_Ritual_JoiningWater"), dict(ritual="Festival"), dict(ritual="Funeral"), dict(ritual="RUT_Ritual_JoiningWater", targetThingId=ring["id"])):
    rs = S.call("jawa/ritual_start", organizer="Human25453", **kw)
    print(kw, rs.get("success"), rs.get("started"), str(rs.get("message"))[:200])
