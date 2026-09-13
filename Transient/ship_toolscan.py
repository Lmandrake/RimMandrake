import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.list_tools() if hasattr(rb, "list_tools") else None
    if tools is None:
        r = rb._request("tools/list", {})
        tools = [t["name"] for t in r.get("tools", [])]
    else:
        tools = [t if isinstance(t, str) else t.get("name") for t in tools]
    hits = [t for t in tools if any(s in t.lower() for s in ("forbid","job","select","gizmo","order","inspect","refuel","fuel"))]
    print(len(tools), "tools; relevant:", hits)
