import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    U="RM_TheUnfinished97170"
    print(str(s.call("jawa/pawn_force_incapacitate",pawn=U))[:300])
    p=(s.call("jawa/pawn_get",pawn=U)["pawns"][0]); print(p["position"])
    cols=[q for q in pawns(s) if q.get("isPlayer") and q["kind"]=="Colonist"]
    c=min(cols,key=lambda q:abs(q["x"]-p["position"]["x"])+abs(q["z"]-p["position"]["z"])); print(c["id"],c["x"],c["z"])
    r=s.call("jawa/ordered_job",pawnId=c["id"],jobDef="RM_SampleDraftprint",targetAId=U,timeoutSeconds=25,waitTicks=60)
    print(r.get("accepted"),r.get("afterJobDef"))
    print("adv",wait(s,1200))
    print(str(things(s,"RM_Draftprint"))[:600])
    print(str(s.call("jawa/inspect_string",defName="RM_Draftprint"))[:900])
