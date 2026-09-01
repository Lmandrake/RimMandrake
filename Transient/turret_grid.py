import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
roster = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_roster.json"))
roster.sort(key=lambda r: (max(r['x'], r['z']), r['defName']))
AX, AZ = 205, 181   # owner's anchor, index 45455 on 250x250
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/pause_game", {})
    placed, failed = [], []
    col, rowmax = 0, 0
    px, pz = AX, AZ
    for r in roster:
        w = max(r['x'], r['z'])
        if col == 10:
            pz -= rowmax + 3; px = AX; col = 0; rowmax = 0
        rowmax = max(rowmax, w)
        cx = px - w // 2; cz = pz - w // 2
        if cx - w//2 < 3 or cz - w//2 < 3:
            failed.append((r['defName'], cx, cz, "off-map")); continue
        try:
            res = rb.call("rimworld/spawn_thing", {"defName": r['defName'], "x": cx, "z": cz})
            ok = res.get("success") is True and res.get("thingId")
            (placed if ok else failed).append((r['defName'], cx, cz, res.get("thingId") or str(res.get("message",""))[:60]))
        except Exception as e:
            failed.append((r['defName'], cx, cz, str(e)[:60]))
        px -= w + 3; col += 1
    print("placed:", len(placed), "failed:", len(failed))
    for f in failed: print("FAIL:", f)
    cells = [{"x": p[1], "z": p[2]} for p in placed]
    try:
        info = rb.call("rimworld/get_cells_info", {"cells": cells})
        rows = info.get("cells", info.get("results", []))
        have = sum(1 for c in rows if c.get("things"))
        print("verify: centers holding a thing:", have, "/", len(rows))
    except Exception as e:
        print("batch verify unavailable:", str(e)[:80])
    xs = [p[1] for p in placed]; zs = [p[2] for p in placed]
    if placed:
        rb.call("rimworld/jump_camera_to_cell", {"x": (min(xs)+max(xs))//2, "z": (min(zs)+max(zs))//2})
        print("grid rect x", min(xs), "-", max(xs), " z", min(zs), "-", max(zs))
