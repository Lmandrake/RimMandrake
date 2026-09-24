import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_things", {"rect": "200,107,20,20", "limit": 50})
    for t in r.get("things", []):
        print(t.get("id"), t.get("def"), t.get("x"), t.get("z"))
