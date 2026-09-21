import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
GROUPS = {"BARE":(145,125),"ROOF":(192,102),"HELM":(150,125),"SYM":(155,125)}
with RimBridge(host, port, token) as rb:
    before = {p["id"] for p in rb.call("jawa/list_pawns", {"faction":"player"}).get("pawns",[])}
    made = {}
    for g,(x,z) in GROUPS.items():
        r = rb.call("jawa/spawn_pawn", {"kindDef":"Colonist","x":x,"z":z,"faction":"player","count":3})
        print(g, r.get("success"), r.get("message"), [p.get("id") for p in (r.get("pawns") or [])])
    after = rb.call("jawa/list_pawns", {"faction":"player"}).get("pawns",[])
    print("total player pawns now:", len(after))
    for p in after:
        if p["id"] not in before:
            print("NEW", p["id"], p["name"], p["x"], p["z"])
