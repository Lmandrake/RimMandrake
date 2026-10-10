import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "Utils"))
import rimbridge_client as rb
h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=60.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    return json.loads(r["content"][0]["text"]) if isinstance(r, dict) and r.get("content") else r
out = {}
for D, (X, Z) in ((1, (30, 60)), (2, (30, 66)), (3, (30, 72)), (4, (30, 78))):
    site = (X - 12, Z - 1, 20, 4)
    call("jawa/clear_area", rect="%d,%d,%d,%d" % site, dryRun=False)
    call("jawa/set_terrain_batch", ops="Soil:%d,%d,%d,%d" % site)
    call("jawa/set_terrain_batch", ops="WaterShallow:%d,%d,3,2" % (X, Z))       # 6-cell limited pond, cap 30
    call("jawa/flowworks_body_report", x=X, z=Z, classify=True)
    for k in range(8):
        call("jawa/flowworks_excavation_drive", x=X - 1 - k, z=Z, deepenLevels=D, setFill=-1)
    call("jawa/flowworks_pulse", count=60, x=0, z=0, w=0, h=0, includeBodies=False)
    r = call("jawa/flowworks_excavation_rect", x=X - 8, z=Z, w=8, h=1, onlyNonZero=False)
    b = call("jawa/flowworks_body_report", x=X + 2, z=Z + 1, classify=False).get("body") or {}
    out[D] = ([(q["d"], q["f"]) for q in r.get("rows") or []], round(b.get("stock") or 0, 2), b.get("activeCellCount"))
    print(D, out[D])
