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
# TryRect CLIPS to the map, so the returned cell coords reveal the real bounds
for probe in ("0,0,400,1", "0,0,1,400"):
    t = call("jawa/get_terrain_layers", rect=probe, limit=400)
    cells = t.get("cells") or []
    if cells:
        xs = [c["x"] for c in cells]; zs = [c["z"] for c in cells]
        print("probe %-10s scanned=%-5s x:%d..%d  z:%d..%d" % (probe, t.get("cellsScanned"), min(xs), max(xs), min(zs), max(zs)))
