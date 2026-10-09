import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
d=S.call("jawa/get_defs",defs="KCSG.StructureLayoutDef/RUT_VaultType2_FleshWeaponLoose_Sealed",fields="defName"); out["layout"]=[d.get("foundCount"),str(d.get("notFound"))[:100],str(d.get("message"))[:100]]
# sleeper hare, tight
with S.Scene("slp2",40,40,14,8) as sc:
    try:
        sc.put("RM_SleeperVenomvine",2,2)
        hid=sc.pawn("Hare",3,2)
        for i in range(3):
            S.run(16)
            h=[t for t in sc.things().get("things") if t.get("id")==hid]
            out["hare%d"%i]=[(h[0]["x"]-sc.x,h[0]["z"]-sc.z)] if h else None
            out["plant%d"%i]=[t["def"] for t in sc.things().get("things") if "Sleeper" in t["def"]]
    except Exception as e: out["ERR_sl"]=str(e)[:200]
# death bursts
for sp in ["AA_GreenGoo","AA_AcanthamoebaGiganteaSmall","AA_AcanthamoebaGiganteaLarge"]:
    with S.Scene("burst",40,40,14,10) as sc:
        try:
            col=sc.colonist(7,8)
            ids=[]
            for i in range(4):
                ids.append(sc.pawn(sp,2+i*2,2,faction="none"))
            sc.pawn("Muffalo",3,4,faction="none")
            S.run(10)
            for i in ids: sc.kill(i)
            S.run(30)
            th=sc.things().get("things") or []
            out[sp]={"filth":sorted(set(t["def"] for t in th if "Filth" in t["def"])),"nfilth":len([t for t in th if "Filth" in t["def"]]),
                 "alive":[t["def"] for t in th if t.get("def") in (sp,"Muffalo")],"corpses":len([t for t in th if "Corpse" in t["def"]])}
            out[sp]["muff_hediffs"]=[ (t["id"]) for t in th if t["def"]=="Muffalo"]
            for t in th:
                if t["def"]=="Muffalo": out[sp]["muff_hed"]=sc.hediffs(t["id"])
        except Exception as e: out[sp]="ERR "+str(e)[:200]
print(json.dumps(out,default=str))
