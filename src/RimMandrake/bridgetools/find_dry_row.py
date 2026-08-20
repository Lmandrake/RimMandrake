import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
info = call("jawa/world_layers")
print("map search for a conduit-legal run of 45 cells")
best = (0, None)
for z in range(20, 240, 7):
    for x0 in (20, 70, 120, 170):
        b = call("jawa/build_check", rect="%d,%d,45,1" % (x0, z), limit=45, **{"def": "PowerConduit"})
        n = b.get("acceptableCells") or 0
        if n > best[0]: best = (n, (x0, z))
        if n == 45:
            print("  FOUND full run at x=%d z=%d" % (x0, z)); sys.exit(0)
print("  best run found: %d/45 at %s" % best)
# what does this map look like overall?
t = call("jawa/get_terrain_layers", rect="%d,%d,45,1" % (best[1][0], best[1][1]), limit=45)
from collections import Counter
print("  terrain there:", dict(Counter(c["top"] for c in t["cells"])))
