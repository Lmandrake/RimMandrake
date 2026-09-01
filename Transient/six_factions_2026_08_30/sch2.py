import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"] in ("jawa/destroy_batch","jawa/destroy_bulk","jawa/map_info"):
            print("###",t["name"]); print(json.dumps((t.get("inputSchema") or {}).get("properties",{}))[:900])
    print("MAPINFO", json.dumps(rb.call("jawa/map_info",{}))[:400])
