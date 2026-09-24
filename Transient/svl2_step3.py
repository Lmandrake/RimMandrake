import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.list_tools()
    names = sorted(t.get("name") for t in tools)
    jawa = [n for n in names if n and n.startswith("jawa/")]
    print("TOTAL_TOOLS", len(names))
    print("JAWA_COUNT", len(jawa))
    print("HAS_INHABITED_CREATE", "jawa/inhabited_settlement_create" in jawa)
