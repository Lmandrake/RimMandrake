import json, sys
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
s = json.load(open("ralph/live/lived_state.json")); ox, oz = s["ox"], s["oz"]
c = B.probe("census")
print(ox, oz, s["look"])
for k in c["edgeHashes"]:
    print(k)
print(c["nodeTypes"], c["strands"], c["cordEdges"])
