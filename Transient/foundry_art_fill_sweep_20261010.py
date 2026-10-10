import json,os,glob,re
A="/mnt/d/Luke/dev/_artpipe/"
cands="RM_BlueIceMeltwaterCan RM_CharLace RM_PillarArmItem RM_CaudalSpringItem RM_EyeburstItem RM_RuqqalFibre RM_FossilDeepStratum RM_GeneSeekerLoaded RM_RawUltracactus RM_VorrelFruit RM_DeltaLoam RM_FE_Fulgurite RM_FE_ScorchFruit RM_DielectricGel RM_Etchant RM_FailedChassis RM_MedicalCoagulant RM_GlowerCrust RM_WreckLichenScrapings RM_DuneCrawler RM_OllimWood RM_PearlLens RM_SunGlass RSW_KraytLens RM_Floatstone RM_Bitumen RM_TarRuinedGoods RM_BrinePlate RM_SootBrick RM_Tekk RM_VitrifiedBezoar RM_WasteCask RM_BrimlockWater RM_DewgourdFruit RM_ChassisCore RM_BladderFruit RM_ContaminantBezoar".split()
done=os.listdir(A+"done"); src=os.listdir(A+"_artsrc")
# sanity probe: a known present subject
probe=[f for f in done if "dosscatch" in f.lower()]
print("PROBE dosscatch hits",len(probe),"v3 hits",len([f for f in done+src if "v3" in f.lower() and "dosscatch" in f.lower()]))
out={}
for c in cands:
    k=c.lower()
    hits=[f for f in done+src if k in f.lower()]
    jobs=[f for f in done if k in f.lower() and f.endswith(".json") and "manifest" not in f]
    v3=[f for f in hits if re.search(r"v3|v4|nooutline|no_outline",f.lower())]
    out[c]={"jobs":jobs[:6],"v3":v3[:4],"nhits":len(hits)}
    print(c,len(hits),"jobs",jobs[:3],"V3",v3[:2])
json.dump(out,open("/home/mandrake/.seat-tmp/FOUNDRY/sweep.json","w"))
