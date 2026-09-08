import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    node = rb.call("rimworld/get_debug_action", {"path": "Actions\\Spawn Pawn..."})
    labels = [c["label"] for c in node["children"]]
    hits = [l for l in labels if "pirate" in l.lower() or "raider" in l.lower() or "bandit" in l.lower()]
    print(hits)
