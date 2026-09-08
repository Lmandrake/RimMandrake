import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/save_game", {"saveName": "DROIDWORKS_DETONATION_REVIEW_1_grid_2026-09-08"})
    print("save_game:", json.dumps(r))
