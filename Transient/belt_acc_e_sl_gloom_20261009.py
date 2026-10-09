import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
with S.Scene("slp3",40,40,30,12) as sc:
    try:
        sc.put("RM_SleeperVenomvine",2,2)
        hid=sc.pawn("Hare",3,2,faction="player")
        for i in range(3):
            S.run(16)
            th=sc.things().get("things") or []
            h=[t for t in th if t.get("id")==hid]
            out["hare%d"%i]=(h[0]["x"]-sc.x,h[0]["z"]-sc.z) if h else None
            out["plant%d"%i]=[t["def"] for t in th if "Sleeper" in t["def"]]
    except Exception as e: out["ERR_sl"]=str(e)[:200]
    try:
        host=sc.pawn("RM_Gloomcast",22,6)
        fol={k: sc.pawn(k,2+i*2,8) for i,k in enumerate(["RM_Chorn","RM_Gennok","RM_Tebbra"])}
        S.run(600)
        for k,p in fol.items():
            r=S.call("jawa/static_call",type="RimMandrake.CreatureBehaviors.RM_PawnJobProof",method="ProofJob",args=p)
            out["job_"+k]=str(r.get("result") or r)[:200]
        out["host"]=host
    except Exception as e: out["ERR_g"]=str(e)[:200]
print(json.dumps(out,default=str))
