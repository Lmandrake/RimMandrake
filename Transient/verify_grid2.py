import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
roster = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_roster.json"))
roster.sort(key=lambda r: (max(r['x'], r['z']), r['defName']))
AX, AZ = 205, 181
centers = []
col, rowmax, px, pz = 0, 0, AX, AZ
for r in roster:
    w = max(r['x'], r['z'])
    if col == 10:
        pz -= rowmax + 3; px = AX; col = 0; rowmax = 0
    rowmax = max(rowmax, w)
    centers.append((r['defName'], px - w // 2, pz - w // 2))
    px -= w + 3; col += 1
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    hits = 0; misses = []
    for name, x, z in centers[::9] + centers[-1:]:
        c = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
        things = [t.get("defName") or t.get("label") for t in c.get("things", [])]
        ok = any(name in (t or "") for t in things)
        hits += ok
        if not ok: misses.append((name, x, z, things[:2]))
        print(("OK " if ok else "MISS"), name, (x, z), things[:2])
    print("hits:", hits)
