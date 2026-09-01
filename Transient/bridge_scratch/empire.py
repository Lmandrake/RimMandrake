import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
def p(t, a):
    try:
        r = rb.call(t, a)
    except Exception as e:
        print("ERR", t, a, e); return None
    return r
with RimBridge(host, port, token) as rb:
    print("=== schema harmony_patches ===")
    for d in rb.list_tools():
        if d.get("name") in ("jawa/harmony_patches","jawa/get_defs"):
            print(d.get("name"), json.dumps(d.get("inputSchema") or d.get("input_schema") or d)[:900])
