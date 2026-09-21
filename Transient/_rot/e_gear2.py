import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for p in ["Human36856","Human36838"]:
        r = rb.call("jawa/thing_stats", {"pawn":p,"slot":"apparel","stats":"RUT_SheenProtection"})
        print(p, json.dumps({k:v for k,v in r.items() if k!="operation"})[:600])
    r = rb.call("jawa/list_pawns", {"faction":"player","includeHealth":True})
    for p in r.get("pawns",[]):
        if p["id"] in ("Human36865","Human36838"):
            hs = [(h.get("def"),h.get("severity")) for h in (p.get("health") or {}).get("hediffs",[])]
            print(p["id"], hs)
