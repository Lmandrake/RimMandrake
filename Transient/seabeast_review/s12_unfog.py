import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb

with rb() as b:
    r = b.call("jawa/set_fog", {"action": "unfogAll"})
    print("UNFOG:", json.dumps({k: v for k, v in r.items() if k != "operation"})[:400])
    b.call("jawa/map_commit", {})
    for (x, z) in [(38, 32), (162, 68), (100, 212)]:
        ci = b.call("rimworld/get_cell_info", {"x": x, "z": z})["cell"]
        print("  ", x, z, "fogged", ci["fogged"], ci["terrainDefName"])
