"""POND_VOLUME A3 tail: an overfull tank (units > capacity) keeps every unit and its inspect line says overfull (old save).
Compressed: the capacity drop an old save causes (300 -> 80) is made here with tankCapacityMultiplier 1 -> 0.5."""
import sys,os,json
sys.path.insert(0, os.path.join(os.getcwd(),"src","RimMandrake","FlowWorks","northstar"))
import proof_hose as PH
B=PH.PB(); S="RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
T=(153,50); out={}
m0=B.call("jawa/mod_settings_field", typeName=S, action="get", field="tankCapacityMultiplier").get("value")
out["fill"]=B.hp("filltank:%d,%d=%s,80"%(T+(PH.LIQUID_WATER,)))
try:
    B.call("jawa/mod_settings_field", typeName=S, action="set", field="tankCapacityMultiplier", value="0.5")
    B.ticks(2)
    out["tank"]=B.hp("tank:%d,%d"%T)
    tid=out["tank"].get("id")
    out["inspect"]=[th.get("inspect") for th in ((B.call("jawa/inspect_string", defName="RM_LiquidTank", rect="%d,%d,2,2"%T, limit=2) or {}).get("things") or [])]
    B.ticks(250)
    out["tank_after_250"]=B.hp("tank:%d,%d"%T)
finally:
    out["restore"]=B.call("jawa/mod_settings_field", typeName=S, action="set", field="tankCapacityMultiplier", value=str(m0)).get("success")
    out["tank_restored"]=B.hp("tank:%d,%d"%T)
print(json.dumps(out,indent=1)[:2500]); json.dump(out,open("overfull.json","w"),indent=1)
