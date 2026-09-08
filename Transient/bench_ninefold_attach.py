import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

TARGETS = [
 ("CompArt","JustCreatedBy"),("CompLaunchable","TryLaunch"),
 ("FireUtility","TryStartFireIn"),("GenExplosion","DoExplosion"),
 ("JobDriver_Deconstruct","FinishedRemoving"),
 ("ListerBuildingsRepairable","Notify_BuildingRepaired"),
 ("MentalBreakWorker_Catatonic","TryStart"),
 ("MentalStateHandler","TryStartMentalState"),
 ("Pawn","Kill"),("Pawn","SetFaction"),
 ("Pawn_GuestTracker","CapturedBy"),("Pawn_HealthTracker","MakeDowned"),
 ("Pawn_RelationsTracker","AddDirectRelation"),
 ("PregnancyUtility","ApplyBirthOutcome"),
 ("ResearchManager","FinishProject"),("TradeDeal","TryExecute"),
]
h,p,t = resolve_endpoint()
hit=miss=0
with RimBridge(h,p,t) as rb:
    for ty, me in TARGETS:
        try:
            r = rb.call("jawa/harmony_patches", {"typeName": ty, "methodName": me})
        except Exception as e:
            print(f"  ERR  {ty}.{me}: {str(e)[:120]}"); miss+=1; continue
        blob = json.dumps(r)
        nine = "inefold" in blob
        owners = sorted(set(json.loads(blob).get("_x", []) )) if False else None
        # pull owner ids / assemblies mentioning ninefold
        import re
        found = sorted(set(re.findall(r'[\w.]*[Nn]inefold[\w.]*', blob)))
        if nine:
            hit+=1; print(f"  OK   {ty}.{me}  <- {', '.join(found[:3])}")
        else:
            miss+=1
            allown = sorted(set(re.findall(r'"owner"\s*:\s*"([^"]+)"', blob)))
            print(f"  MISS {ty}.{me}   patched-by: {allown[:4] if allown else 'NOBODY / method not found'}")
print(f"\nNINEFOLD ATTACHED: {hit}/{len(TARGETS)}   missing {miss}")
