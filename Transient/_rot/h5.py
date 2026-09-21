import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PAWNS=["Human125","Human128","Human122"]
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_batch",{"rects":"118,130,10,8","categories":"All"})
    ch=rb.call("rimworld/list_debug_action_children", {"path":"Actions"})["children"]
    P=next(c["path"] for c in ch if c["path"].endswith("T: Grow plant to maturity"))
    cells=[(120,134),(122,134),(124,134)]
    for x,z in cells:
        rb.call("jawa/spawn_batch",{"ops":"RUT_FalseFruit:%d,%d,1"%(x,z)})
        rb.call("rimworld/execute_debug_action",{"path":P,"x":x,"z":z})
    t=rb.call("jawa/list_things",{"defName":"RUT_FalseFruit"})
    ids=[(q["id"],q["x"],q["z"],q.get("className")) for q in t.get("things",[])]
    print("fruit:",ids)
    rb.call("jawa/set_game_speed",{"speed":"Normal"})
for pid,(tid,x,z,cn) in zip(PAWNS, ids):
    with RimBridge(host, port, token) as rb:
        rb.call("jawa/set_draft",{"pawnId":pid,"drafted":False})
        r=rb.call("jawa/ordered_job",{"pawnId":pid,"jobDef":"Harvest","targetAId":tid,"waitTicks":30,"timeoutSeconds":15})
        print("job",pid,tid,r.get("afterJobDef"),r.get("nowRunningRequested"))
