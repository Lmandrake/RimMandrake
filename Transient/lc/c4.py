import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    c=s.call("jawa/pawn_get",pawn="Human96531")["pawns"][0]; print(c["position"], str(c)[:300])
    u=s.call("jawa/pawn_get",pawn="RM_TheUnfinished97170")["pawns"][0]; print(u["position"])
    r=s.call("rimbridge/list_logs"); 
    for m in r.get("logs",r.get("entries",[]))[-25:]: print(str(m)[:300])
    print(list(r)[:8])
    pj(s.call("jawa/ordered_job",pawnId="Human96531",jobDef="RM_SampleDraftprint",targetAId="RM_TheUnfinished97170",timeoutSeconds=25,waitTicks=30))
