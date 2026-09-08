import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
CELL_X, CELL_Z = 100, 130
OIL_X, OIL_Z = 103, 130

def logs(r):
    return [l["message"] for l in r.get("effects", {}).get("logs", [])]

with RimBridge(host, port, token, timeout=20) as rb:
    print("gate toggle 1 (open->closed):", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: PitCell: toggle gate", "x": CELL_X, "z": CELL_Z})))
    print("report after close:", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Report pit state (RAW)", "x": CELL_X, "z": CELL_Z})))
    print("gate toggle 2 (closed->open):", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: PitCell: toggle gate", "x": CELL_X, "z": CELL_Z})))
    print("report after open:", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Report pit state (RAW)", "x": CELL_X, "z": CELL_Z})))
    print("Oiled ignite:", logs(rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Oiled: ignite (bypasses soaked/Sprung gate)", "x": OIL_X, "z": OIL_Z})))
    r = rb.call("rimworld/get_cell_info", {"x": OIL_X, "z": OIL_Z})
    print("oiled pit cell after ignite:", json.dumps(r.get("cell", {}).get("things")))
