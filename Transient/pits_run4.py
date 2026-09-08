import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CELL_X, CELL_Z = 100, 130
with RimBridge(host, port, token, timeout=20) as rb:
    for i in range(3):
        rb.call("rimworld/execute_debug_action", {"path": "Actions\\Add Prisoner"})
    r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: PitCell: assign nearest prisoner", "x": CELL_X, "z": CELL_Z})
    print("assign:", r.get("effects", {}).get("logs"))
    shot = rb.call("rimworld/take_screenshot", {"fileName": "pits_check_prisoner_1.png"})
    print("screenshot:", json.dumps(shot)[:600])
