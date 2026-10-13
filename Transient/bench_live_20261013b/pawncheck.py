import sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    c = rb.call("rimworld/list_colonists")
    L = rb.call("rimworld/list_letters").get("letters") or []
    mi = rb.call("jawa/map_info")
    bad = [x.get("label") for x in L if x.get("letterDef") in ("Death","GameEnded")]
    print("PAWNCHECK colonists=%s tick=%s map=%s/%s deathLetters=%s letters=%d" % (c.get("count"), mi.get("ticksGame"), mi.get("mapId"), mi.get("mapBiome"), bad, len(L)))
