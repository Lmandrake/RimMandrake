"""LIQUID_RECESSION_TOPOLOGY_1 A1 live probe: a limited dumbbell pond (two 3x3 blobs + a 1-cell bridge) drained by a deep
channel recedes from its outer edge and never leaves two separate wet patches. Reads isSource per cell after each pulse batch."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint()
S = rb.RimBridge(host=h, port=p, token=t, timeout=60.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
X, Z = 60, 20
A = [(X + i, Z + j) for i in range(3) for j in range(3)]
BR = [(X + 3, Z + 1)]
Bb = [(X + 4 + i, Z + j) for i in range(3) for j in range(3)]
POND = A + BR + Bb
CH = [(X - 1 - k, Z + j) for k in range(12) for j in range(3)]
site = (X - 13, Z - 3, 24, 9)
print("clear", call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False).get("success"))
print("soil", call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site).get("success"))
print("water", call("jawa/set_terrain_batch", ops=";".join("WaterShallow:%d,%d,1,1" % c for c in POND)).get("success"))
br = call("jawa/flowworks_body_report", x=X, z=Z, classify=True)
print("body", json.dumps(br.get("body"))[:400])
for c in CH:
    call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=9, setFill=-1)
def wet():
    r = call("jawa/flowworks_excavation_rect", x=X, z=Z, w=7, h=3, onlyNonZero=False)
    m = {(q["x"], q["z"]): q for q in r.get("rows") or []}
    return {c for c in POND if m.get(c, {}).get("isSource")}
def comps(cells):
    cells, n = set(cells), 0
    while cells:
        n += 1; st = [cells.pop()]
        while st:
            c = st.pop()
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    q = (c[0] + dx, c[1] + dz)
                    if q in cells: cells.remove(q); st.append(q)
    return n
hist, worst, bridge_lost_early = [], 1, None
for b in range(40):
    pass
    _b = call("jawa/flowworks_body_report", x=X, z=Z, classify=False).get("body") or {}
    r = call("jawa/flowworks_pulse", count=5, x=0, z=0, w=0, h=0, includeBodies=False)
    w = wet(); k = comps(w)
    worst = max(worst, k)
    if BR[0] not in w and (set(A) & w) and (set(Bb) & w) and bridge_lost_early is None: bridge_lost_early = b
    hist.append((5 * (b + 1), len(w), k, sorted(set(POND) - w), _b.get("activeCellCount"), round(_b.get("stock") or 0, 1)))
    if len(hist) > 3 and hist[-1][1] == hist[-4][1]: break
    if len(w) <= 1: break
br2 = call("jawa/flowworks_body_report", x=X, z=Z, classify=False).get("body") or {}
print("body_after", {k: br2.get(k) for k in ("stock", "capacity", "cellCount", "recededCount", "activeCellCount")})
for row in hist: print("pulse %3d wet %2d comps %d bodyActive(before batch) %s stock %s receded %s" % (row[0], row[1], row[2], row[4], row[5], row[3]))
first = [c for row in hist for c in row[3]]
order = []
for c in first:
    if c not in order: order.append(c)
print("recede order:", order)
print("RESULT", json.dumps({"maxComponents": worst, "bridgeLostWhileBothBlobsWet": bridge_lost_early, "finalWet": hist[-1][1] if hist else None}))
call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
