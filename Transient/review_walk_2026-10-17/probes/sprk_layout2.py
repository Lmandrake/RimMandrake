"""Layout F: pond | pump | pipes with the head on the far pipe; tank beside the first pipe; power south (python.exe). args ox oz"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
ox, oz = int(sys.argv[1]), int(sys.argv[2])
B.call("jawa/destroy_batch", rects="%d,%d,12,10" % (ox - 2, oz - 5), categories="Building,Plant,Item,Filth")
B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,12,10;WaterShallow:%d,%d,2,2" % (ox - 2, oz - 5, ox, oz))
ops = ["RM_LiquidPump:%d,%d" % (ox + 2, oz)] + ["RM_UniversalPipe:%d,%d" % (x, oz) for x in range(ox + 3, ox + 7)] + \
      ["RM_LiquidTank:%d,%d" % (ox + 4, oz + 2), "PowerConduit:%d,%d" % (ox + 2, oz - 1), "PowerConduit:%d,%d" % (ox + 2, oz - 2),
       "Battery:%d,%d,0" % (ox + 2, oz - 4), "RM_SprinklerHead:%d,%d" % (ox + 6, oz)]
r = B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False)
print("build", r.get("survived"), r.get("failed"))
print(B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % (ox + 2, oz - 4)).get("success"))
print(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
             args="%d,%d;Store;RM_Liquid_FreshWater;100000" % (ox + 4, oz + 2)).get("result"))
B.ticks(2600)
ids = ",".join(t["id"] for d in ("RM_SprinklerHead", "RM_LiquidPump", "RM_LiquidTank", "Battery")
               for t in B.call("jawa/list_things", defName=d, rect="%d,%d,12,10" % (ox - 2, oz - 5)).get("things") or [])
for t in B.call("jawa/inspect_string", thingIds=ids).get("things") or []:
    print(t["id"], (t["x"], t["z"]), t["inspect"])
