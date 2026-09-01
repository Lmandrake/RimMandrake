import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb._request("tools/list", {}).get("tools", [])
    for t in tools:
        if t.get("name") in ("rimworld/drag_cell", "rimworld/flood_fill_cells", "rimworld/execute_debug_action"):
            print(t["name"], "schema:", json.dumps(t.get("inputSchema", {}).get("properties", {}))[:400])
