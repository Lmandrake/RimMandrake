import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
DROID_ID = "RSW_DW_Race_guy762_DroidRace_T3series39455"

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:1000])
    return r

with RimBridge(host, port, token) as rb:
    call(rb, "rimworld/select_pawn", {"pawnId": DROID_ID}, "select_pawn")

    wear_root = "Actions" + CH + "Wear apparel (selected)..."
    r = call(rb, "rimworld/get_debug_action", {"path": wear_root}, "get_debug_action wear_root")

    r = call(rb, "rimworld/list_debug_action_children", {"path": wear_root}, "list children of wear_root")
    children = r.get("children", [])
    match = [c for c in children if "DroidHardware_agility" in c.get("path","")]
    print("MATCHES:", match)
