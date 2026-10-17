"""Layout G: tank | pipes x4 continuous, pump built over pipe 2, head on pipe 4; power north (python.exe). args ox oz [pond]"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "RimMandrake", "Utils"))
import validation_core as V
B = V.Bridge()
ox, oz = int(sys.argv[1]), int(sys.argv[2])
B.call("jawa/destroy_batch", rects="%d,%d,12,10" % (ox - 2, oz - 4), categories="Building,Plant,Item,Filth")
B.call("jawa/set_terrain_batch", ops="Soil:%d,%d,12,10" % (ox - 2, oz - 4))
r1 = B.call("jawa/build_batch", ops=";".join(["RM_LiquidTank:%d,%d" % (ox, oz)] + ["RM_UniversalPipe:%d,%d" % (x, oz) for x in range(ox + 2, ox + 6)]),
            faction="player", wipeExisting=False)
r2 = B.call("jawa/build_batch", ops=";".join(["RM_LiquidPump:%d,%d" % (ox + 3, oz), "RM_SprinklerHead:%d,%d" % (ox + 5, oz),
            "PowerConduit:%d,%d" % (ox + 3, oz - 1), "PowerConduit:%d,%d" % (ox + 3, oz - 2), "Battery:%d,%d,0" % (ox + 3, oz - 4)]),
            faction="player", wipeExisting=False)
print("build", r1.get("survived"), r1.get("failed"), r2.get("survived"), r2.get("failed"))
B.call("jawa/gss_stage", ops="kind=gss_charge|x=%d|z=%d" % (ox + 3, oz - 4))
print(B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofTank",
             args="%d,%d;Store;RM_Liquid_FreshWater;100000" % (ox, oz)).get("result"))
B.ticks(2600)
ids = ",".join(t["id"] for d in ("RM_SprinklerHead", "RM_LiquidPump", "RM_LiquidTank")
               for t in B.call("jawa/list_things", defName=d, rect="%d,%d,12,10" % (ox - 2, oz - 4)).get("things") or [])
for t in B.call("jawa/inspect_string", thingIds=ids).get("things") or []:
    print(t["id"], (t["x"], t["z"]), t["inspect"])
