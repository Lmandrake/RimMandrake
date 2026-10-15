import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t,timeout=120.0) as rb:
    c = lambda tool, **kw: rb.call(tool, kw)
    mi = c("jawa/map_info"); print("map", {k: mi.get(k) for k in ("tile","mapId","mapBiome","sizeX","outdoorTempNow")})
    r = c("jawa/list_pawns", faction="hostile", limit=200)
    for pw in r.get("pawns") or []: print("hostile", json.dumps(pw)[:400])
    d = c("jawa/destroy_bulk", filter="nonColonists", dryRun=True); print("dryrun", json.dumps(d)[:800])
    m = c("jawa/list_things", defName="VoidMonolith", limit=10); print("monolith", json.dumps(m)[:600])
