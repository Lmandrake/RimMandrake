import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
for t in ["RimMandrake.StarWars.JawaRules.JawaHoodProof"]:
    r=S.call("jawa/static_call",type=t,method="ProofHood",args="-"); out["hood"]=str(r)[:250]
for sp in ["AA_RedSpore","AA_InfectedAerofleet","AA_Thunderbeast"]:
    with S.Scene("burst",40,40,14,10) as sc:
        try:
            a=sc.pawn(sp,5,5,faction="none")
            m=sc.pawn("Muffalo",6,5,faction="player")
            c0=S.call("jawa/game_condition_list") if False else None
            S.run(5); sc.kill(a); S.run(30)
            th=sc.things().get("things") or []
            out[sp]={"filth":len([t for t in th if "Filth" in t["def"]]),"kinds":sorted(set(t["def"] for t in th if "Filth" in t["def"])),"corpse":[t["def"] for t in th if "Corpse" in t["def"]],"muff":sc.hediffs(m)}
        except Exception as e: out[sp]="ERR "+str(e)[:200]
print(json.dumps(out,default=str))
