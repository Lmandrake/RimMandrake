import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    node = rb.call("rimworld/get_debug_action", {"path": "Actions\\Mental state..."})
    labels = [c["label"] for c in node.get("children", [])]
    hits = [l for l in labels if "graffiti" in l.lower() or "spree" in l.lower() or "rm_" in l.lower()]
    print("mental state hits:", hits)
    print("total mental states:", len(labels))
