import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
TARGETS = {
 "Human36838":(145,125),"Human36841":(146,125),"Human36844":(147,125),
 "Human36847":(192,102),"Human36850":(193,102),"Human36853":(194,102),
 "Human36856":(150,125),"Human36859":(151,125),"Human36862":(152,125),
 "Human36865":(155,125),"Human36868":(156,125),"Human36871":(157,125)}
with RimBridge(host, port, token) as rb:
    h = rb.call("jawa/list_pawns", {"faction":"hostile"})
    print("hostiles:", h.get("message"))
    for pid,(x,z) in TARGETS.items():
        r = rb.call("jawa/order_pawn", {"pawnId":pid,"x":x,"z":z,"draft":True,"waitTicks":600,"unpause":True,"timeoutSeconds":60})
        rows = r.get("pawns") or r.get("results") or []
        print(pid, "->", (x,z), r.get("success"), json.dumps(rows)[:200])
