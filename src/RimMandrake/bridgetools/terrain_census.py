"""Print the current map's top-terrain census. Windows python.exe, repo root:
    python.exe src/RimMandrake/bridgetools/terrain_census.py"""
import sys, json, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
mi = call("jawa/map_info"); sx, sz = mi.get("sizeX"), mi.get("sizeZ")
g = call("jawa/get_terrain_batch", rects="0,0,%d,%d" % (sx, sz)); c = collections.Counter()
for op in (g.get("ops") or "").split(";"):
    if ":" not in op: continue
    d, rect = op.split(":", 1); q = rect.split(",")
    c[d] += int(q[2]) * int(q[3]) if len(q) == 4 else 1
print(mi.get("mapBiome"), sx, sz); print(json.dumps(dict(c.most_common(25))))
