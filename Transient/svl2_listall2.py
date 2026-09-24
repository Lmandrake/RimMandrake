import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.list_tools()
    names = sorted(t.get("name") for t in tools if t.get("name") and t.get("name").startswith("jawa/"))
    for n in names:
        print(n)
