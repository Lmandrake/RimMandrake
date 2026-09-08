import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, cell_center, stage_positions

with rb() as b:
    ci = b.call("rimworld/get_cell_info", {"x": 10, "z": 10})
    print("CELLINFO:", json.dumps(ci)[:600])
    mi = b.call("jawa/map_info", {}) if True else None
    print("MAPINFO:", json.dumps(mi)[:600])
