import sys, json, re, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lay = rb.call("rimworld/get_ui_layout", {})
    s = json.dumps(lay)
    # find actionable elements in the naming dialog
    els = re.findall(r'\{[^{}]*"label"\s*:\s*"[^"]*"[^{}]*\}', s)
    for e in els:
        if any(k in e.lower() for k in ("ok", "accept", "confirm", "random", "name")):
            print(e[:220])
