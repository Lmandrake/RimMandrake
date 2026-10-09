import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
T="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof"
def sc(m,a="0"): return call("jawa/static_call",type=T,method=m,args=a).get("result")
print("ADV",sc("ProofAdvance","16"))
r=call("jawa/list_things",defName="GravEngine",limit=3); print(str(r)[:500])
eid=None
for k in ("things","results"):
    if r.get(k): eid=r[k][0].get("id") or r[k][0].get("thingId")
print("eid",eid)
if eid: print("INSPECT",call("jawa/inspect_string",thing=eid))
print("TEAR",sc("ProofTearFree","0"))
if eid: print("INSPECT2",call("jawa/inspect_string",thing=eid))
