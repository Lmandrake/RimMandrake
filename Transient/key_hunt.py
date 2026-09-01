import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb._request("tools/list", {}).get("tools", [])
    names = [t["name"] for t in tools]
    print([n for n in names if any(k in n for k in ("key", "press", "window", "dialog", "escape", "ui", "close", "input"))])
    # what does the ui state say now
    r = rb.call("rimworld/get_selection_semantics", {})
    print(json.dumps(r.get("uiState", {}))[:400])
