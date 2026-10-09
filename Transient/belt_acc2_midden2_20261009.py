import sys, json, collections
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid); S.quiet()
ms = S.call("jawa/list_things", defName="RM_LongShadeMidden", rect="0,0,120,120", limit=50).get("things") or []
m = ms[0]
before = {t["id"] for t in (S.call("jawa/list_things", rect="%d,%d,9,9" % (m["x"] - 4, m["z"] - 4), limit=100).get("things") or [])}
cols = [p for p in (S.call("jawa/list_pawns", limit=50).get("pawns") or []) if p.get("isPlayer")]
c = cols[-1]["id"]
S.call("jawa/set_game_speed", speed=4)
o = S.call("jawa/ordered_job", pawnId=c, jobDef="RM_SearchMidden", targetAId=m["id"], waitTicks=1500)
S.call("jawa/set_game_speed", speed=0)
print("order", o.get("success"), str(o.get("note"))[:300])
print("comp after", S.call("jawa/comp_read", thing=m["id"], comp="MiddenHeap", members="spent").get("values"))
after = S.call("jawa/list_things", rect="%d,%d,9,9" % (m["x"] - 4, m["z"] - 4), limit=100).get("things") or []
new = [(t.get("def"), t.get("stackCount") or t.get("count")) for t in after if t["id"] not in before]
print("new things", new[:15])
