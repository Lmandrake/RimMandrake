import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
def gd(defs,fields="defName"):
    r=S.call("jawa/get_defs",defs=defs,fields=fields)
    return {"success":r.get("success"),"foundCount":r.get("foundCount"),"notFound":r.get("notFound")}
print("salvage_camp",gd("IncidentDef/RM_WreckFall;IncidentDef/RUT_FallLineWreckFall;ThingDef/RUT_FoundrySalvageCache;ThingSetMakerDef/RUT_SalvageLoot_Foundry;ThingSetMakerDef/RUT_SalvageLoot_Imperial;RimMandrake.Wreckage.RM_WreckListDef/RUT_WreckList_FallLine;RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_FallLine;RimMandrake.Wreckage.RM_WreckWeatheringDef/RUT_WreckWeathering_ForgeWarm"))
print("salvage_rm",gd(";".join("ThingSetMakerDef/RM_SalvageLoot_"+n for n in "Scrap Hull Hull_Rare Tank Tank_Rare Carapace Carapace_Rare Sealed Sealed_Rare GreyShards".split())))
print("ka",gd("FleckDef/RM_Fleck_KineticRing"))
print("sb",json.dumps(S.call("jawa/static_call",type="RimMandrake.Utinni.UnfinishedLine.UnfinishedLineSiteBeatsProof",method="ProofSiteBeats",args="-"),default=str)[:400])
r=S.call("jawa/drain_log"); print("drain",json.dumps(r,default=str)[:1500])
