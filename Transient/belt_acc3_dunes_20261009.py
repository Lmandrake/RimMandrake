import sys
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
T="RimMandrake.MovingDunes.RM_DunesProof"
for m,a in (("ProofTintLayer","0.6,0.4,0.3"),("ProofTintLayer","1,1,1"),("ProofTint","-"),("ProofTintLive","-")):
    r=S.call("jawa/static_call",type=T,method=m,args=a); print(m,a,r.get("success"),str(r.get("result") or r.get("message"))[:400],flush=True)
