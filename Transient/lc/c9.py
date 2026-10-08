import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    c=s.call("jawa/pawn_get",pawn="Human96531")["pawns"][0]; print(c["position"], c.get("currentJob"), [k for k in c if "ob" in k])
    u=s.call("jawa/pawn_get",pawn="RM_TheUnfinished97234")["pawns"][0]; print(u["position"])
    print(str(s.call("jawa/comp_read",thing="RM_TheUnfinished97234",comp="CompRandomizeUnfinished",members="draftprintTaken"))[:400])
