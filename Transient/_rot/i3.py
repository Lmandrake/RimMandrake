import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PLAN=[("Human36856","RUT_Symbiont_Quickflesh"),("Human36859","RUT_Symbiont_Nightwake"),
      ("Human36862","RUT_Symbiont_Sheenblood"),("Human36868","RUT_Tea_AgeReversal")]
with RimBridge(host, port, token) as rb:
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    for pid,d in PLAN:
        p=ps[pid]
        a=rb.call("jawa/pawn_get",{"pawn":pid})
        print("BEFORE",pid,"bioAge",a.get("ageBiologicalYears") or a.get("biologicalAge") or json.dumps({k:v for k,v in a.items() if "ge" in k.lower()})[:200])
        rb.call("jawa/spawn_batch",{"ops":"%s:%d,%d,1"%(d,p["x"],p["z"])})
        rb.call("jawa/set_draft",{"pawnId":pid,"drafted":False})
    print("items:", [(t["id"],t["def"],t["x"],t["z"]) for t in rb.call("jawa/list_things",{"defName":",".join(d for _,d in PLAN)}).get("things",[])])
