import sys; sys.path.insert(0,"Transient/lc")
from h import *
with S() as s:
    allp=pawns(s)
    un=[p for p in allp if p["kindDef"]=="RM_TheUnfinished"]
    print("existing unfinished",[(p["id"],p["x"],p["z"],p.get("faction")) for p in un])
    cols=[p for p in allp if p.get("isPlayer") and p["kind"]=="Colonist"]
    c=cols[0]; print("colonist",c["id"],c["x"],c["z"])
    r=s.call("jawa/spawn_pawn",kindDef="RM_TheUnfinished",x=c["x"]+4,z=c["z"],count=1)
    print(str(r)[:500])
    pid=(r.get("pawns") or [{}])[0].get("id"); print("pid",pid)
    if pid:
        pg=s.call("jawa/pawn_get",pawn=pid); print(str(pg)[:800])
        r=s.call("jawa/ordered_job",pawnId=c["id"],jobDef="RM_SampleDraftprint",targetAId=pid,timeoutSeconds=25)
        print(str(r)[:500])
        print("adv",wait(s,700))
        print(str(things(s,"RM_Draftprint"))[:1500])
        print(str(s.call("jawa/inspect_string",defName="RM_Draftprint"))[:800])
