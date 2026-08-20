import sys, json
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
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

print("== what is actually along row z=100, x=100..140? ==")
t = call("jawa/get_terrain_layers", rect="100,100,41,1", limit=41)
from collections import Counter
c = Counter(x["top"] for x in t["cells"])
print("   terrain:", dict(c))
print("== can a PowerConduit be placed on each of those cells? ==")
b = call("jawa/build_check", rect="100,100,41,1", limit=41, **{"def":"PowerConduit"})
print("   acceptable:", b.get("acceptableCells"), "of", b.get("tested"))
bad = [x for x in (b.get("cells") or []) if not x["canPlace"]]
for x in bad[:5]: print("     blocked:", x["x"], x["z"], x["reason"], x["occupants"])

print("\n== does the router work over a TINY distance? ==")
for d in (1, 2, 5, 10, 20):
    r = call("jawa/connect_cells", **{"from":"100,100","to":"%d,100" % (100+d)})
    print("   dist %-3d success=%s route=%s len=%s  %s" % (
        d, r.get("success"), r.get("route"), r.get("routeLength"), (r.get("message") or "")[:70]))
