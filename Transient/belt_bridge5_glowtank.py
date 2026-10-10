import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=600): return json.dumps(x,default=str)[:n]
X,Z=112,76
print("spawn", j(S.call("jawa/spawn_batch", ops="RM_GlowTank:%d,%d"%(X,Z)),300))
t=(S.call("jawa/list_things", defName="RM_GlowTank", rect="%d,%d,5,5"%(X-2,Z-2)).get("things") or [{}])[0]
tid=t.get("id") or t.get("thingId"); print("tank", tid)
print("refuel", j(S.call("jawa/thing_refuel", thingId=tid, amount=1),300))
print("settings", j(S.call("jawa/mod_settings_field", typeName="RimMandrake.LuminousPigment.LuminousPigmentSettings", action="get", field="tankNeedsWater"),250))
S.run(300)
r=S.call("jawa/inspect_string", thingIds=tid); print("inspect", j(r,1200))
