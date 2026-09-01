import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions"})["children"]
    names = [c["path"].split(chr(92))[-1] for c in ch]
    for n in names:
        if any(k in n.lower() for k in ("roof", "destroy", "remove", "junk", "weather", "fog", "rock")):
            print("-", n)
