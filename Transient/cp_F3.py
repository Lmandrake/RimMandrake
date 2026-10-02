import sys; sys.path.insert(0,"Transient")
from cp_lib import *
def step(n): return call("rimworld/step_game_ticks", ticks=n, pauseFirst=True)
A,B = "Meat_Muffalo11422","Meat_Muffalo11423"
r = call("jawa/ordered_job", pawnId="Human963", jobDef="HaulToCell", targetAId=B, targetBX=134, targetBZ=106, waitTicks=0); print("haul order:", J({k:r.get(k) for k in ("success","accepted","afterJobDef","nowRunningRequested","note","message")},400))
for i in range(10):
    step(60)
    l = call("jawa/list_things", defName="Meat_Muffalo", rect="130,100,12,12")
    ts=[(t.get("id"),t.get("stackCount"),t.get("x"),t.get("z")) for t in (l.get("things") or [])]
    print(i, ts)
    if len(ts)<=1: break
lin = call("jawa/thing_lineage", ids=A+","+B)
for res in lin["results"]:
    print(res["id"], "found", res["found"], "destroyed", res["destroyed"], "stack", res["stackCount"], "fate", res["fate"], "holder", res["holderChain"])
    for e in res["events"]: print("   ", e["seq"], e["tick"], e["kind"], "other", e["otherId"], "count", e["count"], "stackAfter", e["stackAfter"], "holder", e["holder"], e["destroyMode"])
