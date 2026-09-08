import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

cols = call("rimworld/list_colonists", currentMapOnly=True)
c0 = cols["colonists"][0]
print("selecting", c0["name"], c0["pawnId"])
sel = call("rimworld/select_pawn", pawnId=c0["pawnId"])
print("select result:", sel.get("success"))
time.sleep(0.3)

r = call("rimworld/take_screenshot", fileName="rimtheme_gizmo_row.png")
print("gizmo screenshot:", r.get("success"))

pos = c0.get("position", {})
print("pawn position:", pos)
tx, tz = pos.get("x", 0) + 3, pos.get("z", 0) + 3
rc = call("rimworld/right_click_cell", x=tx, z=tz)
print("right click result:", json.dumps(rc)[:300])
time.sleep(0.3)
r2 = call("rimworld/take_screenshot", fileName="rimtheme_float_menu.png")
print("float menu screenshot:", r2.get("success"))
