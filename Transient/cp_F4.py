import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
A,B = "Meat_Muffalo11422","Meat_Muffalo11423"
r = call("jawa/ordered_job", pawnId="Human963", jobDef="Ingest", targetAId=B, count=1, waitTicks=0); print("ingest order:", J({k:r.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested","note","message")},400))
for i in range(8):
    step(120)
    l = call("jawa/list_things", defName="Meat_Muffalo", rect="130,100,12,12")
    print(i, [(t.get("id"),t.get("stackCount")) for t in (l.get("things") or [])])
    if sum(t.get("stackCount") for t in l.get("things",[]))<35: break
lin = call("jawa/thing_lineage", ids=A+","+B)
for res in lin["results"]:
    print(res["id"], "stack", res["stackCount"], "fate", res["fate"])
    for e in res["events"]: print("   ", e["seq"], e["tick"], e["kind"], "other", e["otherId"], "count", e["count"], "stackAfter", e["stackAfter"], "holder", e["holder"], e["destroyMode"])
lin = call("jawa/thing_lineage", ids="Meat_Muffalo11425,Meat_Muffalo99999")
for res in lin["results"]: print(res["id"], "found", res["found"], "fate", res["fate"], [(e["kind"],e["otherId"]) for e in res["events"]])
