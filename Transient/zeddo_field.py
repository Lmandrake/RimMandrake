import sys, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
# the yard composition: core = start candidates; ring = the rest
PLAN = {
  17007: ["Junkyard","AB_DerelictClusters","VEE_MechanoidShipChunks"],   # the Yard itself (start tile)
  1621:  ["Junkyard","AncientWarehouse"],
  17011: ["Junkyard","VEE_MechanoidShipChunks"],
  17008: ["AncientRuins","VEE_MechanoidShipChunks"],
  17009: ["AB_DerelictClusters","AncientRuins"],
  8100:  ["AncientWarehouse"],
  8096:  ["VEE_MechanoidShipChunks"],
  3241:  ["AncientRuins"],
}
with RimBridge(host, port, token) as rb:
    before = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
    bmap = {x["tile"]: sorted(d["def"] for d in x["mutators"]) for x in before["tiles"]}
    for tile, defs in PLAN.items():
        r = rb.call("jawa/world_mutators_set", {"action": "add", "mutators": ",".join(defs), "tiles": str(tile), "readBack": 1})
        assert r.get("success") is True, (tile, r)
    # landmarks for visibility: Ruins x2 + AncientGarrison on the core
    for tile, lm in [(17007, "Ruins"), (17009, "Ruins"), (1621, "AncientGarrison")]:
        r = rb.call("jawa/world_landmarks_set", {"action": "add", "def": lm, "tiles": str(tile), "checkValid": True})
        print("landmark", lm, "on", tile, "->", r.get("added"), r.get("success"))
    rb.call("jawa/world_commit", {})
    after = rb.call("jawa/world_mutators_get", {"range": "0-21871", "limit": 22000})
    amap = {x["tile"]: sorted(d["def"] for d in x["mutators"]) for x in after["tiles"]}
    # whole-planet LOSS diff
    losses = {}
    for t, b in bmap.items():
        a = amap.get(t, [])
        lost = Counter(b) - Counter(a)
        if lost: losses[t] = dict(lost)
    print("tiles with LOST mutators:", len(losses), losses if len(losses) < 12 else "TOO MANY")
    for t in PLAN:
        print(t, "now:", amap[t])
