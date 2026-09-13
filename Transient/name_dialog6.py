import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lay = rb.call("rimworld/get_ui_layout", {})
    s = json.dumps(lay)
    i = s.find('"ui-element:2:6:5"')
    print(s[i-20:i+1100])
