"""Live 4-direction x 2-length channel proof vs PulseOracle(fixed). Run: python.exe Transient/flowworks_live_dirs_20261002.py"""
import json, sys, importlib.util, pathlib
sys.path.insert(0, "src/RimMandrake/Utils")
import rimbridge_client as rb
spec = importlib.util.spec_from_file_location("v2", "src/RimMandrake/FlowWorks/northstar/validation_v2_DRAFT.py")
v2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
info = call("jawa/map_info"); print("map_info keys", {k: info.get(k) for k in ("sizeX","sizeZ","size")})
W = info.get("sizeX") or info["size"]["x"]; H = info.get("sizeZ") or info["size"]["z"]
cz = H // 2 - 10
PULSES = 10
# bodies: west-edge A and east-edge B, 12x12 WaterDeep (limitless: edge, >=50 cells)
A = (0, cz, 12, 12); B = (W - 12, cz, 12, 12)
scenes = {}
def run(x, z, n, dx, dz): return [(x + dx*i, z + dz*i) for i in range(n)]
for n in (3, 6):
    k = 2 if n == 3 else 8
    scenes[("E", n)] = run(12, cz + k, n, 1, 0)
    scenes[("N", n)] = run(k, cz + 12, n, 0, 1)
    scenes[("S", n)] = run(k, cz - 1, n, 0, -1)
    scenes[("W", n)] = run(W - 13, cz + k, n, -1, 0)
# clear: Soil over everything incl margins, then water bodies
allc = [c for v in scenes.values() for c in v]
x0 = 0; x1 = W
ops = ["Soil:%d,%d,%d,%d" % (0, cz - 12, 30, 36), "Soil:%d,%d,%d,%d" % (W - 30, cz - 12, 30, 36),
       "WaterDeep:%d,%d,%d,%d" % A, "WaterDeep:%d,%d,%d,%d" % B]
r = call("jawa/set_terrain_batch", ops=";".join(ops)); print("terrain", r.get("success"), str(r)[:200])
for c in allc:
    r = call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=1, setFill=-1)
    if not (r.get("success") and r.get("depth") == 1): print("DRIVE FAIL", c, str(r)[:300])
for nm, c in (("A", (A[0]+5, A[1]+5)), ("B", (B[0]+5, B[1]+5))):
    b = call("jawa/flowworks_body_report", x=c[0], z=c[1], classify=True); print("body", nm, json.dumps(b.get("body"))[:300])
def read():
    out = {}
    for k, cs in scenes.items():
        rr = call("jawa/flowworks_excavation_rect", x=min(c[0] for c in cs), z=min(c[1] for c in cs),
                  w=max(c[0] for c in cs)-min(c[0] for c in cs)+1, h=max(c[1] for c in cs)-min(c[1] for c in cs)+1)
        m = {(q["x"], q["z"]): q["f"] for q in rr["rows"]}
        out[k] = [m[c] for c in cs]
    return out
live = {k: [] for k in scenes}
print("pulse0", read())
for p in range(PULSES):
    call("jawa/flowworks_pulse", count=1, x=scenes[("E",3)][0][0], z=scenes[("E",3)][0][1], w=1, h=1)
    rd = read()
    for k in scenes: live[k].append(rd[k])
res = {}
mism = 0
for k, cs in scenes.items():
    o = v2.PulseOracle(W, H, {c: 0 for c in (A and [(x, z) for x in range(A[0], A[0]+12) for z in range(A[1], A[1]+12)] + [(x, z) for x in range(B[0], B[0]+12) for z in range(B[1], B[1]+12)])},
                       {0: {"limitless": True, "stock": 0.0}}, algo="fixed")
    for c in cs: o.dig(c, 1)
    pred = o.run(cs, PULSES)
    ok = pred == live[k]; mism += (not ok)
    print(k, "MATCH" if ok else "MISMATCH")
    for p in range(PULSES): print("  p%-2d live %s  oracle %s %s" % (p+1, live[k][p], pred[p], "" if live[k][p]==pred[p] else "<<<"))
    # first pulse where full
    res[k] = next((p+1 for p in range(PULSES) if live[k][p] == [1]*len(cs)), None)
print("fill-complete pulse:", {"%s%d" % k: v for k, v in res.items()})
for n in (3, 6):
    print("len", n, "identical across dirs:", len({json.dumps(live[(d, n)]) for d in "ENWS"}) == 1)
print("TOTAL MISMATCH scenes:", mism)
