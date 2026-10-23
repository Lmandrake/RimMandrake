import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    r = rb._request("tools/list", {})
    for x in r.get("tools") or []:
        if x.get("name") in sys.argv[1:]:
            print(x["name"], json.dumps(x.get("inputSchema") or x.get("parameters"))[:900]); print((x.get("description") or "")[:500])
