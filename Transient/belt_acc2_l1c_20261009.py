import sys,json,time
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
def sc(t,m,a="-"):
    r=S.call("jawa/static_call",type=t,method=m,args=a)
    return {"success":r.get("success"),"result":r.get("result"),"msg":str(r.get("message"))[:200]}
def gd(defs,fields="defName"):
    r=S.call("jawa/get_defs",defs=defs,fields=fields)
    return {"success":r.get("success"),"foundCount":r.get("foundCount"),"notFound":r.get("notFound"),"rows":[ (x.get("defName"),x) for x in (r.get("defs") or r.get("results") or [])][:30]}
out["bazaar_seeds"]=gd(";".join("RimMandrake.Bazaar.RM_BazaarSeedRuleDef/RM_BazaarSeed_"+n for n in("DesertWater","BrineSalt","PropaneFuel","BoilingSeaStill")))
import re
src=open("src/RimMandrake/Ninefold/Defs/RM_GodFavourTilts.xml",encoding="utf-8").read()
tilts=re.findall(r"<defName>([^<]+)</defName>",src)
out["tilts"]=gd(";".join("RimMandrake.Ninefold.RM_GodFavourTiltDef/"+t for t in tilts))
out["rites"]=gd("PreceptDef/RUT_Ritual_NineFaults;RitualPatternDef/RUT_NineFaultsPattern;RitualBehaviorDef/RUT_NineFaultsBehavior;RitualOutcomeEffectDef/RUT_NineFaultsOutcome;RitualObligationTargetFilterDef/RUT_FreshFind;TaleDef/RUT_GaveTheNineFaults;ThoughtDef/RUT_GaveTheFirstSpark")
out["empire"]=gd(";".join("RuthlessPursuingMechanoids.RUT_EmpireRungDef/RUT_EmpireRung_"+n for n in("Probe","Spotter","Strike","Cordon","Breach","Bombardment")),"rungIndex,kind")
out["illisk"]=gd("PawnKindDef/RM_Illisk")
out["elder"]=sc("RimMandrake.DivingInteraction.RM_ElderTradeUtility","ProofTreasures")
out["dunes"]=sc("RimMandrake.MovingDunes.RM_DunesProof","ProofTint")
out["limbs"]=sc("RimMandrake.FeverWood.RM_FeverWoodProof","ProofLimbs")
out["gizmo"]=sc("RimMandrake.Utinni.WasteRun.WasteRunProof","ProofGizmo")
r=S.call("jawa/map_comp_read",comp="TentacleWatch",members="encounterPressure,sentinelCount"); out["tentacle_mapcomp"]=json.dumps(r,default=str)[:500]
out["smoke_start"]=sc("JawaBench.BridgeTools.JawaBenchSettingsSmoke","Start")
time.sleep(3)
out["smoke_result"]=sc("JawaBench.BridgeTools.JawaBenchSettingsSmoke","Result")
out["probe"]=sc("RimMandrake.ExplosiveKnockback.RM_PatchApplierProbe","Probe")
for k,v in out.items(): print(k,json.dumps(v,default=str)[:700])
json.dump(out,open("Transient/belt_acc2_l1c_raw_20261009.json","w"),indent=1,default=str)
