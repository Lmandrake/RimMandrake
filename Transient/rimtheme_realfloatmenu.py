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
c = cols["colonists"]
print("colonists:", [(p["name"], p["pawnId"]) for p in c])
call("rimworld/select_pawn", pawnId=c[0]["pawnId"])
time.sleep(0.2)
# right-click on the SECOND colonist to get a social/order float menu
rc = call("rimworld/right_click_cell", targetPawnId=c[1]["pawnId"])
print("right click on pawn result:", json.dumps(rc)[:400])
time.sleep(0.4)
r = call("rimworld/take_screenshot", fileName="rimtheme_real_float_menu.png")
print("screenshot:", r.get("success"))
