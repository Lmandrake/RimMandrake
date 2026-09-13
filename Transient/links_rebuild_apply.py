import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
P = r"D:\Luke\dev\Rimworld\Transient\final_review\links_rebuilt.csv"
with RimBridge(host, port, token) as rb:
    dry = rb.call("jawa/world_links_import", {"path": P, "expectTiles": 21872})
    print("DRY:", {k: dry.get(k) for k in ("success","rows","rivers","roads","nonAdjacentRefused")}, "unknownDefs:", dry.get("unknownDefs"))
    assert dry.get("success") is True and not dry.get("unknownDefs") and dry.get("nonAdjacentRefused", 1) == 0, dry
    ap = rb.call("jawa/world_links_import", {"path": P, "apply": True, "clearFirst": True, "expectTiles": 21872})
    print("APPLY:", {k: ap.get(k) for k in ("success","rows","rivers","roads","nonAdjacentRefused")})
    assert ap.get("success") is True, ap
    c = rb.call("jawa/world_commit", {})
    print("commit:", c.get("success"))
    v = rb.call("jawa/world_links_get", {"range": "0-21871", "onlyLinked": True, "limit": 25000})
    json.dump(v.get("tiles"), open(r"D:\Luke\dev\Rimworld\Transient\final_review\links_after_rebuild.json","w"))
    print("re-exported", len(v.get("tiles", [])), "link tiles")
