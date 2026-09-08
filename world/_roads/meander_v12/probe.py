import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.list_tools()
    out = []
    for t in tools:
        n = t.get('name') if isinstance(t, dict) else str(t)
        if 'world' in n or 'link' in n:
            out.append(t)
    json.dump(out, open(r"world\_roads\meander_v12\_tools_world.json", 'w'), indent=1, default=str)
    print("total tools", len(tools), "world-ish", len(out))
    for t in out:
        n = t.get('name') if isinstance(t, dict) else str(t)
        print(" ", n)
