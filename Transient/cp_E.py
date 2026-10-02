import sys; sys.path.insert(0,"Transient")
from cp_lib import *
for dn, dl in (("FarmAnimalsWanderIn",50000),("WandererJoin",51000),("FarmAnimalsWanderIn",52000)):
    r = call("jawa/incident_schedule", incidentDef=dn, delayTicks=dl); print("sched", dn, r.get("success"), r.get("message") or J(r,200))
def q(): 
    p = call("jawa/incident_queue_peek"); return p
p = q(); print("peek count", p["count"], [(x["index"],x["defName"],x["fireTick"],x["ticksUntilFire"]) for x in p["queue"]])
fts = [x["fireTick"] for x in p["queue"] if x["defName"]=="FarmAnimalsWanderIn"]
r = call("jawa/incident_queue_remove", defName="FarmAnimalsWanderIn", fireTick=fts[0]); print("dry:", r.get("success"), r.get("dryRun"), "matched", r.get("matchedCount"), "removed", r.get("removedCount"), "before/after", r.get("countBefore"), r.get("countAfter"))
print("peek after dry:", q()["count"])
r = call("jawa/incident_queue_remove", defName="FarmAnimalsWanderIn", fireTick=fts[0], dryRun=False); print("real:", r.get("success"), "matched", r.get("matchedCount"), "removed", r.get("removedCount"), "before/after", r.get("countBefore"), r.get("countAfter"), "remaining", [(x["defName"],x["fireTick"]) for x in r.get("remaining",[])])
p = q(); print("peek after real:", p["count"], [(x["defName"],x["fireTick"]) for x in p["queue"]])
r = call("jawa/incident_queue_remove", defName="WandererJoin", fireTick=12345, dryRun=False); print("nomatch (fireTick mismatch):", J({k:r.get(k) for k in ("success","message","error")},400))
r = call("jawa/incident_queue_remove", defName="NoSuchIncidentXYZ", dryRun=False); print("nomatch (bad def):", J({k:r.get(k) for k in ("success","message")},300))
r = call("jawa/incident_queue_remove", dryRun=False); print("no selector:", J({k:r.get(k) for k in ("success","message")},300))
print("final peek", q()["count"])
