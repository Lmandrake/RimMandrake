import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    for pid in ("Human661","RM_TheUnfinished97170"):
        r=s.call("jawa/pawn_get",pawn=pid); p=(r.get("pawns") or [{}])[0]; print(pid,p.get("position"),[h["def"] for h in p.get("hediffs",[])],p.get("dead"))
    print(str(s.call("rimworld/list_messages"))[:1200])
    r=s.call("jawa/comp_read",thing="RM_TheUnfinished97170",comp="RimMandrake.Contagion.CompRandomizeUnfinished",members="draftprintTaken"); print(str(r)[:600])
    print(str(s.call("jawa/drain_log"))[:1500])
