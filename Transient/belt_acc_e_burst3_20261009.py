import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
for sp in ["AA_AcanthamoebaGiganteaSmall","AA_AcanthamoebaGiganteaLarge","AA_RedGoo"]:
    with S.Scene("burst",40,40,14,10) as sc:
        try:
            a=sc.pawn(sp,5,5,faction="none")
            m=sc.pawn("Muffalo",6,5,faction="player")
            S.run(5)
            r=sc.kill(a); out[sp+"_kill"]=str(r)[:200]
            ps=S.call("jawa/pawn_get",pawn=a); out[sp+"_state"]=str(ps)[:250]
            S.run(30)
            th=sc.things().get("things") or []
            out[sp]={"filth":sorted(set(t["def"] for t in th if "Filth" in t["def"])),"n":len([t for t in th if "Filth" in t["def"]]),"corpse":[t["def"] for t in th if "Corpse" in t["def"]],"muff":sc.hediffs(m),"things":sorted(set(t["def"] for t in th))}
        except Exception as e: out[sp]="ERR "+str(e)[:200]
print(json.dumps(out,default=str))
