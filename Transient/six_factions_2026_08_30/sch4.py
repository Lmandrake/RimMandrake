import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"]=="jawa/faction_relations_set":
            print(json.dumps((t.get("inputSchema") or {}).get("properties",{}), indent=1)[:1400])
