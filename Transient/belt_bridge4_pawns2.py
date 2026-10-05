import json, sys
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
import validation_v2 as v
B = v.RealBridge()
r = B.call("jawa/list_pawns", includeHealth=True, includeCorpses=True, limit=500)
for p in r.get("pawns") or []:
    if p.get("dead") or p.get("downed"):
        print(p["id"], p.get("x"), p.get("z"), "dead" if p.get("dead") else "downed", json.dumps(p.get("health"))[:700])
