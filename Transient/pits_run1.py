import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

CELL_X, CELL_Z = 100, 130
OIL_X, OIL_Z = 103, 130

def show(label, r):
    print(f"--- {label} ---")
    print(json.dumps(r, indent=2)[:1500])

with RimBridge(host, port, token, timeout=20) as rb:
    show("cell_info before", rb.call("rimworld/get_cell_info", {"x": CELL_X, "z": CELL_Z}))
    show("spawn PitCell", rb.call("rimworld/spawn_thing", {"defName": "RM_PitCell_Single", "x": CELL_X, "z": CELL_Z}))
    show("spawn OiledPit", rb.call("rimworld/spawn_thing", {"defName": "RM_OpenPit_Oiled", "x": OIL_X, "z": OIL_Z}))
    show("add prisoner", rb.call("rimworld/execute_debug_action", {"path": "Actions\\Add Prisoner"}))
