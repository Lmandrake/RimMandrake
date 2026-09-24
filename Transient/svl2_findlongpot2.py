import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    print("TOTAL", len(lp.get("pawns", [])))
    for p in lp.get("pawns", []):
        print(p.get("id"), p.get("name"), p.get("faction"), "dead=", p.get("dead"), "downed=", p.get("downed"))
