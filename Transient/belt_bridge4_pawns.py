import json, sys, collections
sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar")
import validation_v2 as v
B = v.RealBridge()
r = B.call("jawa/list_pawns", includeHealth=False, includeCorpses=True, limit=500)
c = collections.Counter()
for p in r.get("pawns") or []:
    c[(p.get("def"), p.get("faction"), p.get("dead"), p.get("downed"))] += 1
    if p.get("faction") not in (None, "none") or p.get("dead"):
        print({k: p.get(k) for k in ("id", "def", "faction", "dead", "downed", "position", "hostile", "spawned")})
print(sorted(c.items(), key=lambda kv: -kv[1])[:25])
print(list((r.get("pawns") or [{}])[0].keys()))
