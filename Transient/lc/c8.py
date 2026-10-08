import sys; sys.path.insert(0,"Transient/lc")
from h import *
def silver(s):
    r=things(s,"Silver"); return sum(t.get("stackCount",0) for t in r.get("things",[]))
with S() as s:
    up=s.call('jawa/pawn_get',pawn='RM_TheUnfinished97234')['pawns'][0]['position']
    cols=[q for q in pawns(s) if q.get('isPlayer') and q['kind']=='Colonist' and not q.get('downed') and not q.get('dead')]
    C=min(cols,key=lambda q:abs(q['x']-up['x'])+abs(q['z']-up['z'])); print('using',C['id'],C['x'],C['z'],len(cols))
    r=s.call("jawa/ordered_job",pawnId=C["id"],jobDef="RM_SampleDraftprint",targetAId="RM_TheUnfinished97234",timeoutSeconds=25,waitTicks=30); print(r.get("accepted"),r.get("afterJobDef"))
    wait(s,2000)
    ps=things(s,"RM_Draftprint").get("things",[]); print([(p["id"],p["label"]) for p in ps])
    new=[p for p in ps if p["id"]!="RM_Draftprint97213"]
    s0=silver(s); print("silver before",s0)
    if new:
        pid=new[0]["id"]
        s.call("jawa/select_things",action="select",ids=pid)
        g=s.call("rimworld/list_selected_gizmos")["gizmos"]
        t=[x for x in g if x["label"].startswith("Transmit")][0]; print("gizmo",t["disabled"],t.get("disabledReason"),t["description"][:250])
        if not t["disabled"]:
            r=s.call("rimworld/execute_gizmo",gizmoId=t["id"]); print(str(r)[:300])
            wait(s,2000)
            print("silver after",silver(s)); print("print left",[p["id"] for p in things(s,"RM_Draftprint").get("things",[])])
            q=s.call("jawa/quest_lifecycle"); print(str(q)[:700])
