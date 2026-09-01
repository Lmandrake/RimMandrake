import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ids = json.load(open(r"D:\Luke\dev\Rimworld\Transient\teardown_ids.json"))
roster = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_roster.json"))
DROP_MODS = ("Vanilla Furniture Expanded - Props and Decor", "Vanilla Factions Expanded - Pirates",
             "Fortifications - Industrial", "MiningCo. DrillTurret (Continued)")
VFES_KEEP = {"VFES_Turret_ChargeRailgun", "VFES_Turret_Ballista", "VFES_Turret_TeslaBlaster"}
keep = [r for r in roster if r['mod'] not in DROP_MODS
        and (not r['defName'].startswith("VFES_") or r['defName'] in VFES_KEEP)]
keep.sort(key=lambda r: (max(r['x'], r['z']), r['defName']))
print("filtered roster:", len(keep))
DESTROY = "Actions" + chr(92) + "T: Destroy"
host, port, token = resolve_endpoint()
def destroy_all(rb, idlist, tag):
    ok = bad = 0
    for i, tid in enumerate(idlist):
        try:
            r = rb.call("rimworld/execute_debug_action", {"path": DESTROY, "thingId": "Thing_" + tid})
            ok += 1 if r.get("success") else 0
            bad += 0 if r.get("success") else 1
        except Exception:
            bad += 1
        if (i+1) % 300 == 0: print(tag, i+1, "done", flush=True)
    print(tag, "destroyed ok:", ok, "failed:", bad, flush=True)
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/pause_game", {})
    destroy_all(rb, ids["turrets"], "turrets")
    destroy_all(rb, ids["pad"], "pad")
    # centered grid on the pad (85..165 x 95..151), rows of 8
    placed, failed = [], []
    AX, AZ = 90, 148   # top-left, rows go south (z decreasing)
    col, rowmax, px, pz = 0, 0, AX, AZ
    for r in keep:
        w = max(r['x'], r['z'])
        if col == 8:
            pz -= rowmax + 3; px = AX; col = 0; rowmax = 0
        rowmax = max(rowmax, w)
        cx, cz = px + w // 2, pz - w // 2
        try:
            res = rb.call("rimworld/spawn_thing", {"defName": r['defName'], "x": cx, "z": cz})
            (placed if res.get("success") and res.get("thingId") else failed).append((r['defName'], cx, cz, res.get("thingId")))
        except Exception as e:
            failed.append((r['defName'], cx, cz, str(e)[:50]))
        px += w + 3; col += 1
    print("placed:", len(placed), "failed:", len(failed))
    for f in failed: print("FAIL:", f)
    good = 0
    for name, x, z, tid in placed[::6] + placed[-1:]:
        ti = rb.call("rimworld/get_map_target_info", {"thingId": tid})
        good += 1 if ti.get("success") else 0
    print("thingId verify sample:", good, "/", len(placed[::6] + placed[-1:]))
    xs=[p[1] for p in placed]; zs=[p[2] for p in placed]
    rb.call("rimworld/jump_camera_to_cell", {"x": (min(xs)+max(xs))//2, "z": (min(zs)+max(zs))//2})
    print("grid rect x", min(xs), "-", max(xs), " z", min(zs), "-", max(zs))
