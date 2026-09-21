import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PLAN=[("Human36859","RUT_Symbiont_Quickflesh"),("Human36862","RUT_Symbiont_Nightwake"),
      ("Human36844","RUT_Symbiont_Sheenblood"),("Human36838","RUT_Tea_AgeReversal")]
def pinfo(rb,pid):
    p=rb.call("jawa/pawn_get",{"pawn":pid})["pawns"][0]
    return {"bioAge":p["ageBiologicalYears"],"pos":p["position"],"dev":p["developmentalStage"]}
with RimBridge(host, port, token) as rb:
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player","includeHealth":True}).get("pawns",[])}
    items={}
    for pid,d in PLAN:
        p=ps[pid]
        print("BEFORE",pid,pinfo(rb,pid), sorted(h["def"] for h in (p.get("health") or {}).get("hediffs",[])))
        rb.call("jawa/spawn_batch",{"ops":"%s:%d,%d,1"%(d,p["x"],p["z"])})
        rb.call("jawa/set_draft",{"pawnId":pid,"drafted":False})
    for t in rb.call("jawa/list_things",{"defName":",".join(d for _,d in PLAN)}).get("things",[]):
        items.setdefault(t["def"],[]).append(t["id"])
    print("items:",items)
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
for pid,d in PLAN:
    with RimBridge(host, port, token) as rb:
        tid=items[d].pop(0)
        r=rb.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"Ingest","targetAId":tid,"waitTicks":30,"timeoutSeconds":15})
        print("ingest",pid,d,r.get("afterJobDef"),r.get("nowRunningRequested"),str(r.get("note"))[:100])
