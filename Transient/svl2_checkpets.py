import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    for p in lp.get("pawns", []):
        if p.get("id") in ("AA_Eyeling669122", "RSW_Dewback669123"):
            print(json.dumps(p)[:800])
