import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rbc
host, port, token = rbc.resolve_endpoint()
with rbc.RimBridge(host, port, token, timeout=120.0) as rb:
    print("map", {k:v for k,v in rb.call("jawa/map_info",{},check=False).items() if k in("mapBiome","tile","sizeX","mapId")})
    for d in ("RM_MercyLedge","RM_MercyCarving","RM_ChimeLineAnchor"):
        r = rb.call("jawa/list_things", {"defName": d, "limit": 200}, check=False)
        print(d, r.get("success"), r.get("count", r.get("total")), str(r)[:200])
