"""seam.py x z : dig a 3x3 pit at (x..x+2, z..z+2) to D4, cover it with woven scrap, shoot it at play zoom and close up."""
import sys, time, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fwb
from story1 import shot, log
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
x0, z0 = int(sys.argv[1]), int(sys.argv[2])
cells = [(x, z) for x in range(x0, x0 + 3) for z in range(z0, z0 + 3)]
view = (x0 - 5, z0 - 4, 13, 11)
shot(B, "seam_00_before", rect=view)
for c in cells:
    B.call("jawa/clear_area", rect="%d,%d,1,1" % c, dryRun=False)
    B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
r = B.call("jawa/build_batch", ops=";".join("RM_PitCover_WovenScrap:%d,%d" % c for c in cells), faction="player", readBack=1) or {}
log("cover", {k: r.get(k) for k in ("success", "placed", "survived", "failed") if k in r})
B.call("rimworld/play_for", durationMs=500, speed="Normal")
shot(B, "seam_01_play", rect=view)
shot(B, "seam_02_close", rect=(x0 - 1, z0 - 1, 5, 5), root=4.5)
shot(B, "seam_03_maxzoom11", rect=(x0 - 3, z0 - 2, 9, 7), root=11)
