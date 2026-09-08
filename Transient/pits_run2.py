import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
CELL_X, CELL_Z = 100, 130
OIL_X, OIL_Z = 103, 130

def show(label, r):
    print(f"--- {label} ---")
    logs = r.get("effects", {}).get("logs") if isinstance(r.get("effects"), dict) else None
    print("effects.logs:", logs)
    print(json.dumps({k:v for k,v in r.items() if k not in ("state","stateBefore","stateAfter","operation","source")}, indent=2)[:1200])

with RimBridge(host, port, token, timeout=20) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Report pit state (RAW)", "x": CELL_X, "z": CELL_Z})
    show("report pitcell (before assign)", r)
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: PitCell: assign nearest prisoner", "x": CELL_X, "z": CELL_Z})
    show("assign nearest prisoner", r)
