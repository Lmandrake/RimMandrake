import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ts = rb.list_tools()
    names = sorted(t.get("name") for t in ts)
    print(len(names))
    for n in names:
        if any(k in n for k in ("faction","log","raid","pawn","incident","relation")):
            print(n)
