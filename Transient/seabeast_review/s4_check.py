import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\Transient\seabeast_review")
from sb_common import rb, CREATURES, stage_positions, grid_label

pts = []
for i, c in enumerate(CREATURES):
    for s, (x, z) in enumerate(stage_positions(i)):
        pts.append((c[0], s, x, z))

bad = []
with rb() as b:
    for name, s, x, z in pts:
        ci = b.call("rimworld/get_cell_info", {"x": x, "z": z})["cell"]
        if ci["terrainDefName"] != "Sand" or not ci["walkable"] or ci["thingCount"]:
            bad.append((name, s, x, z, ci["terrainDefName"], ci["walkable"], ci["thingCount"]))
print("checked", len(pts), "bad", len(bad))
for r in bad:
    print("  ", r)
