"""Try a sprinkler layout B at origin x z: tank, 4 pipes in a line, head on the last pipe, pump off the line on pipe 2 (python.exe)."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
ox, oz = int(sys.argv[1]), int(sys.argv[2])
B.call("jawa/destroy_batch", rects="%d,%d,10,9" % (ox - 2, oz - 2), categories="Building,Plant,Item,Filth")
ops = ["RM_LiquidTank:%d,%d" % (ox, oz)] + ["RM_UniversalPipe:%d,%d" % (x, oz) for x in range(ox + 2, ox + 6)] + \
      ["RM_LiquidPump:%d,%d" % (ox + 3, oz + 1), "PowerConduit:%d,%d" % (ox + 4, oz + 1), "Battery:%d,%d,0" % (ox + 5, oz + 2),
       "RM_SprinklerHead:%d,%d" % (ox + 5, oz)]
B.call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,2,2" % (ox + 2, oz + 2))
r = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
print("build", r.get("survived"), r.get("failed"))
B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % (ox + 5, oz + 2))
print(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
             args="%d,%d;Store;RM_Liquid_FreshWater;100000" % (ox, oz)).get("result"))
B.ticks(2600)
heads = B.call("jawa/list_things", defName="RM_SprinklerHead", rect="%d,%d,1,1" % (ox + 5, oz)).get("things") or []
pumps = B.call("jawa/list_things", defName="RM_LiquidPump", rect="%d,%d,1,1" % (ox + 3, oz + 1)).get("things") or []
ids = ",".join(t["id"] for t in heads + pumps)
for t in B.call("jawa/inspect_string", thingIds=ids).get("things") or []:
    print(t["id"], t["inspect"])
