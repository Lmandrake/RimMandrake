import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CH = chr(92)
DROID_ID = "RSW_DW_Race_guy762_DroidRace_T3series39455"
DROID_THING_ID = "Thing_" + DROID_ID

def call(rb, tool, args=None, label=None):
    r = rb.call(tool, args or {})
    print(f"--- {label or tool} ---")
    print(json.dumps(r)[:1500])
    return r

with RimBridge(host, port, token) as rb:
    call(rb, "rimworld/select_pawn", {"pawnId": DROID_THING_ID}, "select_pawn with Thing_ prefix")

    r = call(rb, "jawa/pawn_get", {"pawn": DROID_ID}, "pawn_get BEFORE wear")
    hediffs_before = r.get("hediffs") or r.get("pawn", {}).get("hediffs")
    print("hediffs_before:", hediffs_before)
