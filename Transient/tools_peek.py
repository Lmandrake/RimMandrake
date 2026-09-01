import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tools = rb.call("rimbridge/list_tools", {})
    import json
    names = [t.get("name") for t in tools.get("tools", [])] if isinstance(tools, dict) else []
    for n in names:
        if any(k in (n or "") for k in ("faction","destroy","pawn_health","damage","list_pawns")):
            print(n)
