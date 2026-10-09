import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
call=S.call
T="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof"
def sc(m,a="0"): return call("jawa/static_call",type=T,method=m,args=a).get("result")
print("ADV",sc("ProofAdvance","16")[:60])
r=call("jawa/inspect_string",thingIds="GravEngine38028"); print("ENG",json.dumps(r)[:600])
print("TEAR",sc("ProofTearFree","0")[:60])
r=call("jawa/inspect_string",thingIds="GravEngine38028"); print("ENG2",json.dumps(r)[:600])
