import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
with S.Scene("dw",80,200,12,8) as sc:
    sc.room()
    r=S.call("jawa/spawn_pawn",kindDef="RSW_DW_OuterRim_ProtocolDroid",x=sc.x+5,z=sc.z+4,faction="player",count=1)
    out["spawn"]=str(r)[:300]
    pid=(r.get("pawns") or [{}])[0].get("id")
    if pid:
        S.run(60)
        g=S.call("jawa/pawn_get",pawn=pid); p=(g.get("pawns") or [{}])[0]
        out["keys"]=list(p.keys())[:40]
        out["hediffs0"]=str([ (h.get("def"),h.get("severity")) for h in p.get("hediffs",[])])
        out["needs0"]=str(S.call("jawa/pawn_need",pawn=pid,action="list"))[:600]
        def tier(sev):
            S.call("jawa/pawn_health",pawn=pid,action="remove",hediff="RSW_DW_FormatTier")
            S.call("jawa/pawn_health",pawn=pid,action="add",hediff="RSW_DW_FormatTier",severity=sev)
            S.run(30)
            h=[(x.get("def"),x.get("severity")) for x in ((S.call("jawa/pawn_get",pawn=pid).get("pawns") or [{}])[0].get("hediffs",[])) if x.get("def")=="RSW_DW_FormatTier"]
            n=[x["need"] for x in S.call("jawa/pawn_need",pawn=pid,action="list").get("needs",[])]
            return dict(h=h,needs=n)
        for sev in (2,1,3,4,2): out["tier%s_%d"%("",sev)+("b" if "tier_2" in out and sev==2 else "")]=tier(sev)
        S.kill(sc,pid) if False else sc.kill(pid)
print(json.dumps(out,default=str))
