import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
DROID_ID = "RSW_DW_Race_guy762_DroidRace_T3series39455"

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:1200])
    return r

with RimBridge(host, port, token) as rb:
    r = call(rb, "jawa/list_pawns", {}, "list_pawns re-check")
    droid = next((p for p in r.get("pawns", []) if p.get("id") == DROID_ID), None)
    print("droid now:", droid)

    call(rb, "rimworld/select_pawn", {"pawnId": DROID_ID}, "select_pawn retry2")

    r = call(rb, "jawa/pawn_health", {"pawn": DROID_ID, "action": "get"}, "pawn_health BEFORE wear (correct param)")
