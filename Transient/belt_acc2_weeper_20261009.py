import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LeaningScrub.RM_LeaningScrubSettings"
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid); S.quiet()
def pools(rect):
    r = S.call("jawa/list_things", defName="RM_VenomPool", rect=rect, limit=100)
    return r.get("countMatched"), len(r.get("things") or [])
# open ground near middle
S.call("jawa/clear_area", rect="40,40,30,30")
S.call("jawa/set_terrain_batch", ops="Soil:40,40,30,30")
A = ";".join("RM_WeeperVenomvine:%d,%d,1,1" % (45 + 4 * i, 45) for i in range(6))
B = ";".join("RM_WeeperVenomvine:%d,%d,1,1" % (45 + 4 * i, 62) for i in range(6))
for ops in (A,):
    r = S.call("jawa/set_plants", ops=ops, growth=1.0); print("plant A", r.get("success"), str(r.get("message"))[:120])
print("before", pools("40,40,30,12"))
with S.setting(SET, weeperEnabled=True, modEnabled=True):
    S.run(8000)
    print("on 8000t", pools("40,40,30,12"), flush=True)
    S.run(12000)
    print("on 20000t", pools("40,40,30,12"), flush=True)
r = S.call("jawa/set_plants", ops=B, growth=1.0); print("plant B", r.get("success"), str(r.get("message"))[:100])
with S.setting(SET, weeperEnabled=False):
    S.run(20000)
    print("off 20000t B-area", pools("40,57,30,12"), "A-area(on-earlier)", pools("40,40,30,12"), flush=True)
