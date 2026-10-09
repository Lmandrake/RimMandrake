import json, os, re, sys
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from scenes import scenelib as S
O={}
r=S.call("jawa/get_defs", defs="IncidentDef/PsychicDrone;IncidentDef/PsychicSoothe;GameConditionDef/PsychicDrone;GameConditionDef/PsychicSoothe;GameConditionDef/PsychicDroner;GameConditionDef/PsychicSuppression;IncidentDef/PsychicEmanatorShipPartCrash", fields="label,description,letterText")
O["force"]=r
src=open("src/RimMandrake/Ninefold/Defs/RM_GodFavourTilts.xml",encoding="utf-8").read()
tilts=re.findall(r"<defName>([^<]+)</defName>",src)
r=S.call("jawa/get_defs", defs=";".join("RimMandrake.Ninefold.RM_GodFavourTiltDef/"+t for t in tilts), fields="defName")
O["tilts_full"]={k:(r.get(k) if isinstance(r,dict) else None) for k in("success","foundCount","notFound")}
r=S.call("jawa/get_defs", defs="ThingDef/RUT_FoundrySalvageCache", fields="defName")
O["cache"]=r
r=S.call("jawa/harmony_patches", typeName="GravshipUtility", methodName="PreLaunchConfirmation"); O["launch"]=r
d=S.call("jawa/drain_log", limit=400, errorsOnly=True)
msgs=[m.get("text","") for m in d.get("messages",[])]
O["ek_errs"]=[m[:200] for m in msgs if "ExplosiveKnockback" in m or "RM_Knockback" in m]
O["gss_errs"]=[m[:200] for m in msgs if "GimmeSomeSlack" in m]
O["n_drain"]=len(msgs)
json.dump(O,open("Transient/belt_acc_l1b_raw_20261009.json","w"),indent=1,default=str)
