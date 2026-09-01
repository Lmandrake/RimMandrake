import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
big = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_data.json"))
CUT = {"BreadMoAM_Turret_LargeShotgun", "VQE_AncientSpacerAutocannon"}
big = [r for r in big if r['defName'] not in CUT]
def sz(r):
    if 'size' in r and isinstance(r['size'], str):
        a, b = r['size'].split('x'); return max(int(a), int(b))
    return max(r.get('x', 1), r.get('z', 1))
big.sort(key=lambda r: (sz(r), r['defName']))
small = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_1x1.json"))
small.sort(key=lambda r: (r['mod'], r['defName']))
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/pause_game", {})
    gi = rb.call("rimworld/get_game_info", {})
    print("ticksGame:", gi.get("ticksGame"), "maps:", gi.get("mapCount"))
    placed, failed = [], []
    AX, AZ = 6, 243   # upper-left with margin
    px, pz, col, rowmax = AX, AZ, 0, 0
    for r in big:
        w = sz(r)
        if col == 10:
            pz -= rowmax + 3; px = AX; col = 0; rowmax = 0
        rowmax = max(rowmax, w)
        cx, cz = px + w // 2, pz - w // 2
        try:
            res = rb.call("rimworld/spawn_thing", {"defName": r['defName'], "x": cx, "z": cz})
            (placed if res.get("success") and res.get("thingId") else failed).append((r['defName'], cx, cz, res.get("thingId") or str(res.get("message", ""))[:50]))
        except Exception as e:
            failed.append((r['defName'], cx, cz, str(e)[:50]))
        px += w + 3; col += 1
    pz -= rowmax + 5
    for i, r in enumerate(small):
        cx, cz = AX + (i % 15) * 3, pz - (i // 15) * 4
        try:
            res = rb.call("rimworld/spawn_thing", {"defName": r['defName'], "x": cx, "z": cz})
            (placed if res.get("success") and res.get("thingId") else failed).append((r['defName'], cx, cz, res.get("thingId") or str(res.get("message", ""))[:50]))
        except Exception as e:
            failed.append((r['defName'], cx, cz, str(e)[:50]))
    print("placed:", len(placed), "failed:", len(failed))
    for f in failed: print("FAIL:", f)
    good = 0; sample = placed[::8] + placed[-1:]
    for name, x, z, tid in sample:
        ti = rb.call("rimworld/get_map_target_info", {"thingId": tid})
        good += 1 if ti.get("success") else 0
    print("thingId verify:", good, "/", len(sample))
    zs = [p[2] for p in placed]
    rb.call("rimworld/jump_camera_to_cell", {"x": 30, "z": (max(zs) + min(zs)) // 2})
    time.sleep(0.4)
    print(rb.call("rimworld/take_screenshot", {}).get("path"))
