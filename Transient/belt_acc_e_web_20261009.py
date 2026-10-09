import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out=[]
for i in range(4):
    r=S.call("jawa/static_call",type="RimMandrake.Webwork.RM_WebworkProof",method="ProofHarvest",args="true;RM_Webwork_Anchor;34")
    out.append(str(r.get("result") or r)[:200] if isinstance(r,dict) else str(r)[:200])
r=S.call("jawa/static_call",type="RimMandrake.Webwork.RM_WebworkProof",method="ProofHarvestDesignate",args="RM_Webwork_Anchor"); out.append(str(r.get("result") or r)[:200])
print(json.dumps(out))
