"""Step the pond_pump site one flow pulse at a time until a pond cell reads RM_WaterThin (python.exe). args: rect maxpulses"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
rect, n = sys.argv[1], int(sys.argv[2])
for i in range(n):
    ops = B.call("jawa/get_terrain_batch", rects=rect).get("ops")
    wet = [o for o in ops.split(";") if not o.startswith("Soil")]
    print(i, wet, flush=True)
    if "RM_WaterThin" in ops:
        break
    B.ticks(250)
B.call("rimworld/set_time_speed", speed=0)
