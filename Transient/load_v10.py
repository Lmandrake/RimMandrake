import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("rimworld/load_game", {"saveName": "WORLDMAP_V10_cathedral_landmarks_2026-09-07"})
    print("load_game response:", json.dumps(r)[:400])
