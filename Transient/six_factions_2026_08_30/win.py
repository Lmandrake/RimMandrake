import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        if t["name"]=="jawa/window_list_close":
            print("SCHEMA", json.dumps((t.get("inputSchema") or {}).get("properties",{}))[:700]); print()
    r=rb.call("jawa/window_list_close", {})
    print(json.dumps({k:v for k,v in r.items() if k!="operation"}, ensure_ascii=False, indent=1)[:2500])
