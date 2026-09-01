import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        c = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
        print("colonists:", str(c)[:200])
    except Exception as e:
        print("colonists ERR", str(e)[:100])
    try:
        rb.call("jawa/clear_ui", {})
        s = rb.call("rimworld/take_screenshot", {})
        print("shot:", s.get("path") or str(s)[:200])
    except Exception as e:
        print("shot ERR", str(e)[:100])
