"""POND_RECESSION_STRANDS_CHANNEL_1 regression (L2): a 6-cell LIMITED pond (3x2, cap 30) with an 8-cell channel dug
west from its SW corner at depth 1..4 must keep draining: the inlet cell (the pond cell whose cardinal neighbour is the
first channel cell) stays a source while the body has stock, and the pond gives more than the 6 units it gave before the
fix (recession dried the inlet second, cutting the channel off with ~80% stranded).
python.exe, bridge held, any quicktest map. The site must be UNTOUCHED (re-running on a dug site deepens it further and
reuses the old body): pass a fresh base as argv "X,Z" (default 110,60; uses x X-12..X+7, z Z-1..Z+20). Exit 0 = PASS, 1 = FAIL."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=120.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
CAP = 30.0
BX, BZ = (int(v) for v in (sys.argv[1] if len(sys.argv) > 1 else "110,60").split(","))
fails, rows = [], {}
for D, (X, Z) in ((1, (BX, BZ)), (2, (BX, BZ + 6)), (3, (BX, BZ + 12)), (4, (BX, BZ + 18))):
    site = (X - 12, Z - 1, 20, 4)
    call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
    call("jawa/set_roof_batch", ops="None:%d,%d,%d,%d" % site)
    call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
    call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % (X, Z))
    call("jawa/flowworks_body_report", x=X, z=Z, classify=True)
    for k in range(8):
        call("jawa/flowworks_excavation_drive", x=X - 1 - k, z=Z, deepenLevels=D, setFill=-1)
    call("jawa/flowworks_pulse", count=60, x=0, z=0, w=0, h=0, includeBodies=False)
    r = call("jawa/flowworks_excavation_rect", x=X - 8, z=Z, w=8, h=1, onlyNonZero=False)
    b = call("jawa/flowworks_body_report", x=X + 2, z=Z + 1, classify=False).get("body") or {}
    inlet = call("jawa/flowworks_excavation_report", x=X, z=Z)
    stock = b.get("stock")
    fills = [(q.get("d"), q.get("f")) for q in r.get("rows") or []]
    inlet_src = inlet.get("isSourceCell")
    drained = None if stock is None else round(CAP - stock, 2)
    rows[D] = dict(fills=fills, stock=stock, active=b.get("activeCellCount"), inletSource=inlet_src, drained=drained)
    print(D, rows[D])
    if stock is None:
        fails.append("D%d: no body read (UNMEASURED)" % D)
        continue
    if stock > 0 and inlet_src is not True:
        fails.append("D%d: inlet (%d,%d) not a source with stock %.1f left" % (D, X, Z, stock))
    if drained <= 6.5:
        fails.append("D%d: pond gave only %.1f units (pre-fix stranding)" % (D, drained))
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
