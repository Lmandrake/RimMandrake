import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    for i in range(6):
        c=s.call("jawa/pawn_get",pawn="Human96531")["pawns"][0]
        print(i,s._ticks(),c["position"],[h["def"] for h in c.get("hediffs",[])][:4])
        wait(s,300)
    print(str(things(s,"RM_Draftprint"))[:300])
