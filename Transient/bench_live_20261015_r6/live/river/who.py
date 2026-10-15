import sys, os, json
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
with RimBridge(h, p, t) as rb:
    r = rb.call("jawa/list_pawns", {"limit": 400})
for x in r.get("pawns") or []:
    if str(x.get("id","")).endswith(sys.argv[1]): print(json.dumps(x)[:600])
