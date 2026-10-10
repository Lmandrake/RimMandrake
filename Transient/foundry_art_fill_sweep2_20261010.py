import os,re,json
A="/mnt/d/Luke/dev/_artpipe/"
done=[f for f in os.listdir(A+"done") if f.endswith(".json") and ".manifest" not in f]; src=os.listdir(A+"_artsrc")
cands="RM_HalfExtractedCore RM_BellowsItem RM_SweetlineWool RSW_Apparel_FangPendant RM_Drazz RM_VorrelSeedDish RM_TetchikJar RM_VisslerArm RM_MurrinCatch RM_SandSieve RM_FossilSkeleton RM_ShullaCatch RM_ZennaqFilament RM_Biosilica RSW_MarshFungus RUT_PilgrimJournal RUT_Mindstone RUT_SealedWaterJar RUT_CrackWax RUT_MetalSaltBezoar RM_Saal RM_Deepfire RM_CaudalSpringItem RM_EyeburstItem RM_FossilDeepStratum RM_GeneSeekerLoaded RM_FailedChassis RM_WreckLichenScrapings RSW_KraytLens RM_TarRuinedGoods RM_BrimlockWater RM_ChassisCore RM_ContaminantBezoar".split()
print("probe",len([f for f in done if "dosscatch" in f.lower()]))
for c in cands:
    k=c.lower(); j=[f for f in done if k in f.lower()]; v=[f for f in j+src if re.search("v3|v4|nooutline",f.lower()) and k in f.lower()]
    print(c,"jobs",j[:3],"V3" if v else "-")
