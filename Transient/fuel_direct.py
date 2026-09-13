import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb._request("tools/list", {})
    tools = [t["name"] for t in r.get("tools", [])]
    print("fuel/comp tools:", [t for t in tools if any(s in t.lower() for s in ("fuel","comp","refuel","designat"))])
    # designations on the minified corner
    d = rb.call("jawa/designate_batch", {"action": "list", "rect": "225,1,20,15"})
    print("designations near corner:", str(d)[:200])
