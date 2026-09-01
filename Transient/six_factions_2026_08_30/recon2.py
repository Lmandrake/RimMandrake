import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = [t["name"] for t in rb.list_tools()]
    jawa = sorted(n for n in tools if n.startswith("jawa/"))
    print("TOTAL", len(tools), "JAWA", len(jawa))
    print("JAWA_TOOLS:", " ".join(jawa))
