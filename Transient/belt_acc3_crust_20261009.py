import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
P=lambda m,a="": str((S.call("jawa/static_call",type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",method=m,args=a) or {}).get("result"))[:400]
sc=S.Scene("crust",40,60,11,11)
sc.__enter__()
sc.room(roof=True,floor="Substructure")
sc.put("GravEngine",5,5)
sc.put("Door",5,0,stuff="BlocksGranite")
sc.colonist(2,2)
S.call("jawa/map_commit",full=True)
print("state",P("ProofState"))
print("adv",P("ProofAdvance","16"))
print("tear",P("ProofTearFree"))
