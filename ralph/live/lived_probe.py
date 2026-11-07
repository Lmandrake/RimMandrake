import json, sys
sys.path.insert(0, "src/RimMandrake/GimmeSomeSlack/northstar_matrix"); sys.path.insert(0, "src/RimMandrake/Utils")
import run_live as RL
B = RL.LiveBridge()
s = json.load(open("ralph/live/lived_state.json")); ox, oz = s["ox"], s["oz"]
def rd(tag):
    m = B.probe("motion"); c = B.probe("census")
    print(tag, {k: m.get(k) for k in ("liveFloorEnds","deadFloorEnds","liveEndsAll","whipTails")}, {k: c.get(k) for k in ("builds","conduitCells","cordEdges","pending")}, "ends", len(c.get("ends") or []), json.dumps(c.get("ends") or [])[:400])
print(B.probe("doorstrays"))
rd("before")
B.probe("rebuild")
rd("rebuilt")
print(ox, oz)
