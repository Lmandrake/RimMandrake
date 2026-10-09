import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
print(S.call("jawa/static_call",type="RimMandrake.MovingDunes.RM_DunesProof",method="ProofTint",args="-").get("result"))
