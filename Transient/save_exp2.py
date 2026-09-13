import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    s = rb.call("rimworld/save_game", {"saveName": "EXPERIMENTAL_shipcrewed_2026-09-09"})
    print("save:", s.get("saveName"), s.get("sizeBytes"))
