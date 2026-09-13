import sys, json, re
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lay = rb.call("rimworld/get_ui_layout", {})
    s = json.dumps(lay)
    i = s.find("NamePlayerGravship")
    print(s[max(0,i-200):i+2200] if i >= 0 else "dialog not in layout; total len %d" % len(s))
