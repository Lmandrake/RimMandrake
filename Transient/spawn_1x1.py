import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
BS = chr(92)
roster = json.load(open(r"D:\Luke\dev\Rimworld\Transient\turret_1x1.json"))
roster.sort(key=lambda r: (r['mod'], r['defName']))
with RimBridge(host, port, token) as rb:
    rb.call("rimworld/pause_game", {})
    placed, failed = [], []
    x0, z0 = 90, 112
    for i, r in enumerate(roster):
        cx, cz = x0 + (i % 15) * 3, z0 - (i // 15) * 4
        try:
            res = rb.call("rimworld/spawn_thing", {"defName": r['defName'], "x": cx, "z": cz})
            (placed if res.get("success") and res.get("thingId") else failed).append((r['defName'], res.get("thingId") or str(res.get("message",""))[:50]))
        except Exception as e:
            failed.append((r['defName'], str(e)[:50]))
    print("1x1 placed:", len(placed), "failed:", len(failed))
    for f in failed: print("FAIL:", f)
    # one-shot cleanups
    for act in ("Destroy non-colonists", "Destroy fire", "Clear All Fog", "Clear Junk"):
        r = rb.call("rimworld/execute_debug_action", {"path": "Actions" + BS + act})
        print(act, "->", r.get("success"), str(r.get("message",""))[:60])
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions" + BS + "Change weather..."})
    clear = [c["path"] for c in ch.get("children", []) if c["path"].split(BS)[-1] in ("Clear", "Clear\t (clear)")]
    if not clear:
        clear = [c["path"] for c in ch.get("children", []) if "clear" in c["path"].split(BS)[-1].lower()]
    if clear:
        r = rb.call("rimworld/execute_debug_action", {"path": clear[0]})
        print("weather clear ->", r.get("success"))
    # paint the whole map grass: activate rect tool once, then corner pairs in 20-row bands
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions" + BS + "Set terrain (rect)..." + BS + "VFEArch_Grass"})
    print("grass tool:", r.get("success"))
    for zb in range(0, 250, 25):
        z2 = min(zb + 24, 249)
        rb.call("rimworld/click_cell", {"x": 0, "z": zb})
        rb.call("rimworld/click_cell", {"x": 249, "z": z2})
    print("painted 10 bands")
    time.sleep(0.5)
    s = rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path"))
