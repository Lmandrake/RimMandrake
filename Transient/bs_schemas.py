import sys; sys.stdout.reconfigure(encoding="utf-8")
import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
want=set(sys.argv[1:])
with RimBridge(h,p,t) as rb:
    for x in rb.list_tools():
        if x.get("name") in want:
            print(x["name"], (x.get("description") or "")[:500].replace("\n"," "), json.dumps((x.get("inputSchema") or {}).get("properties",{}))[:700])
            print()
