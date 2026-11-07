import json, sys
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
r = B.call("jawa/list_things", defName="PowerConduit", limit=300)
S={(t["x"],t["z"]) for t in r["things"]}
for z in range(137,115,-1):
    print("%3d "%z + "".join("#" if (x,z) in S else "." for x in range(138,190)))
