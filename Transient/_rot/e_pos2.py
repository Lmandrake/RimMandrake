import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
T={"Human36850":(193,102),"Human36853":(194,102),"Human36865":(155,125)}
with RimBridge(host, port, token) as rb:
    for pid,(x,z) in T.items():
        r = rb.call("jawa/order_pawn", {"pawnId":pid,"x":x,"z":z,"draft":True,"waitTicks":1200,"unpause":True,"timeoutSeconds":90})
        print(pid, r.get("success"), json.dumps(r.get("pawns"))[:230])
    # final positions + roofed check
    ALL=["Human36838","Human36841","Human36844","Human36847","Human36850","Human36853","Human36856","Human36859","Human36862","Human36865","Human36868","Human36871"]
    ps={p["id"]:p for p in rb.call("jawa/list_pawns", {"faction":"player"}).get("pawns",[])}
    for pid in ALL:
        p=ps.get(pid,{}); x,z=p.get("x"),p.get("z")
        ci=rb.call("rimworld/get_cell_info", {"x":x,"z":z})["cell"]
        print(pid, p.get("name"), (x,z), "roof=", ci.get("roofDefName"))
