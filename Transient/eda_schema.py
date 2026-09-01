import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb._request("tools/list", {}).get("tools", [])
    t = next(t for t in tools if t["name"] == "rimworld/execute_debug_action")
    print(json.dumps(list(t.get("inputSchema", {}).get("properties", {}).keys())))
