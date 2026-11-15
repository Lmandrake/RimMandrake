import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
S="RimMandrake.Pyrelands.RM_PyrelandsSettings"; BL="RimMandrake.Pyrelands.MapComponent_BurnLine"
with RimBridge(h,p,tk) as rb:
    prior=rb.call("jawa/mod_settings_field",{"typeName":S,"action":"get","field":"fireClockEnabled"}).get("value")
    rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":"fireClockEnabled","value":"True"})
    rb.call("jawa/map_fire",{"action":"extinguish","rect":"0,0,250,250"})
    print("rearm", rb.call("jawa/static_call",{"type":BL,"method":"RearmOpeningFront"}).get("result"))
    rb.call("jawa/safe_advance",{"ticks":360,"timeException":False})
    print("probe", rb.call("jawa/static_call",{"type":BL,"method":"ProbeOpeningFront"}).get("result"))
    fr=[f for f in rb.call("jawa/list_things",{"defName":"Fire","limit":2000}).get("things") or [] if not f.get("parent")]
    print("freeStandingFires", len(fr))
    rb.call("jawa/map_fire",{"action":"extinguish","rect":"0,0,250,250"})
    rb.call("jawa/mod_settings_field",{"typeName":S,"action":"set","field":"fireClockEnabled","value":str(prior)})
