import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for pid,(x,z) in {"Human36856":(149,133),"Human36859":(150,133)}.items():
        r=rb.call("jawa/order_pawn",{"pawnId":pid,"x":x,"z":z,"draft":True,"waitTicks":900,"unpause":True,"timeoutSeconds":60})
        print(pid, (r.get("pawns") or [{}])[0].get("arrived"), (r.get("pawns") or [{}])[0].get("end"))
    ALL="Human36838 Human36841 Human36844 Human36847 Human36850 Human36853 Human36856 Human36859 Human36862 Human36865 Human36868 Human36871".split()
    for p in ALL:
        rb.call("jawa/set_draft",{"pawnId":p,"drafted":True})
        rb.call("jawa/pawn_health",{"pawn":p,"action":"remove","hediff":"RUT_SheenCoating"})
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    for pid in ALL:
        p=ps[pid]; ci=rb.call("rimworld/get_cell_info",{"x":p["x"],"z":p["z"]})["cell"]
        print(pid,(p["x"],p["z"]),"roof",ci.get("roofDefName"))
