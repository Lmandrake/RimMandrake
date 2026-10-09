import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for m,a in (("ProofState","x"),("ProofTearFree","x"),("ProofState","x")):
    print(m,json.dumps(S.call("jawa/static_call",type="RimMandrake.TerminalBiomes.RM_GreyHullCrustProof",method=m,args=a))[:600])
