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
if not sx or not sz: sys.exit("jawa/map_info gave no map size (%s) - no current map?" % str(mi)[:200])
# get_terrain_batch refuses more than 70,000 cells per call (MaxCells, JawaBenchTerrainTools.cs) with no ops at all,
# so one whole-map rect could never read a 275x275 or larger map: read in z-bands that each fit under the cap.
band = max(1, 70000 // sx); c = collections.Counter(); g = {}
for z0 in range(0, sz, band):
    g = call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z0, sx, min(band, sz - z0)))
    for op in (g.get("ops") or "").split(";"):
        if ":" not in op: continue
        d, rect = op.split(":", 1); q = rect.split(",")
        c[d] += int(q[2]) * int(q[3]) if len(q) == 4 else 1
print(mi.get("mapBiome"), sx, sz); print(json.dumps(dict(c.most_common(25))))
n = sum(c.values())   # an errored or out-of-bounds read returns no ops: an empty census is a blind instrument, not an empty map
if n != sx * sz: print("census covers %d of %d cells - NOT a full read: %s" % (n, sx * sz, str(g)[:200])); sys.exit(1)
