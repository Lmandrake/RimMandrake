import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CELL_X, CELL_Z = 100, 130
with RimBridge(host, port, token, timeout=20) as rb:
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Spawn Pawn...\\Pirate", "x": 97, "z": 128})
    print("spawn pirate:", json.dumps(r)[:600])
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\Add Prisoner"})
    print("add prisoner:", json.dumps(r.get("effects"))[:400])
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: PitCell: assign nearest prisoner", "x": CELL_X, "z": CELL_Z})
    print("assign:", r.get("effects", {}).get("logs"))
