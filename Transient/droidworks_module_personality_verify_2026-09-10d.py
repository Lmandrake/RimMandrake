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
    call(rb, "jawa/set_pawn_faction", {"pawn": DROID_ID, "faction": "PlayerColony"}, "set_pawn_faction")
    call(rb, "rimworld/select_pawn", {"pawnId": DROID_ID}, "select_pawn (retry)")

    wear_path = "Actions" + CH + "Wear apparel (selected)..." + CH + "RSW_DW_Module_DroidHardware_agility"
    call(rb, "rimworld/execute_debug_action", {"path": wear_path}, "wear module")

    time.sleep(1)
    r = call(rb, "jawa/pawn_health", {"pawnId": DROID_ID}, "pawn_health after wear")
