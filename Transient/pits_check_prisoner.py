import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    for tool in ["jawa/list_pawns", "rimworld/list_colonists"]:
        try:
            r = rb.call(tool, {})
            print(tool, json.dumps(r)[:2500])
        except Exception as e:
            print(tool, "EXC", e)
