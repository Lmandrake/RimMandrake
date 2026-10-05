import json, sys
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
import validation_v2 as v
B = v.RealBridge()
r = B.call("jawa/flowworks_pit_report", x=166, z=100)
print(r.get("descentCount"), r.get("recentDescents"))
