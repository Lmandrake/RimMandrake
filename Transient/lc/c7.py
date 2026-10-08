import sys; sys.path.insert(0,"Transient/lc")
from h import *
def silver(s):
    r=things(s,"Silver"); return sum(t.get("stackCount",0) for t in r.get("things",[]))
with S() as s:
    allp=pawns(s)
    c=[q for q in allp if q["id"]=="Human96531"][0]
    r=s.call("jawa/spawn_pawn",kindDef="RM_TheUnfinished",x=c["x"]+2,z=c["z"]+2,count=1); U=r["pawns"][0]["id"]; print(U,r["pawns"][0]["kindActual"])
    s.call("jawa/pawn_force_incapacitate",pawn=U)
    for h in ("RM_UnfinishedClaw","RM_UnfinishedVestigialWing"):
        print(str(s.call("jawa/pawn_health",action="add",pawn=U,hediff=h,severity=0.5))[:200])
    print([x["def"] for x in s.call("jawa/pawn_get",pawn=U)["pawns"][0]["hediffs"]])
    pos=s.call("jawa/pawn_get",pawn=U)["pawns"][0]["position"]; print(pos)
    s0=silver(s); print("silver before",s0)
    r=s.call("jawa/ordered_job",pawnId=c["id"],jobDef="RM_SampleDraftprint",targetAId=U,timeoutSeconds=25,waitTicks=30); print(r.get("accepted"))
    wait(s,900)
    ps=things(s,"RM_Draftprint").get("things",[]); print([(p["id"],p["label"]) for p in ps])
    new=[p for p in ps if p["id"]!="RM_Draftprint97213"]
    if new:
        pid=new[0]["id"]
        s.call("jawa/select_things",action="select",ids=pid)
        g=s.call("rimworld/list_selected_gizmos")["gizmos"]
        t=[x for x in g if x["label"].startswith("Transmit")][0]; print("gizmo",t["disabled"],t.get("disabledReason"),t["description"][:200])
        if not t["disabled"]:
            r=s.call("rimworld/execute_gizmo",gizmoId=t["id"]); print(str(r)[:300])
            wait(s,1500)
            print("silver after",silver(s)); print("print left",[p["id"] for p in things(s,"RM_Draftprint").get("things",[])])
            q=s.call("jawa/quest_lifecycle"); print(str(q)[:600])
