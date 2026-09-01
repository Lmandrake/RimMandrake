import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.list_tools()
    names = sorted(d.get("name") for d in tools)
    print("TOOLCOUNT:", len(names))
    print("JAWA:", len([n for n in names if n.startswith("jawa/")]))
    for kw in ("harmony","scen","reflect","invoke","eval","screenshot","camera","world_render","mode","load_game","save"):
        print(kw.upper(), ":", [n for n in names if kw in n.lower()])
