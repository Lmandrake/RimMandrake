import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})
    kids = ch.get("children", [])
    print("count", len(kids))
    for c in kids:
        print(c["path"])
    print("=== Show more actions ===")
    ch2 = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Show more actions"})
    for c in ch2.get("children", []):
        print(c["path"])
