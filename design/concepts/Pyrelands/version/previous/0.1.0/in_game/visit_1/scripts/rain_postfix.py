"""Owed RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST live: a forced ordinary rain, rolled through WeatherDecider, must come out RM_FE_BlackRain."""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint(); out={}
with RimBridge(h,p,tk) as rb:
    # SITE: the quiet profile's Tutor storyteller makes ChooseNextWeather return Clear before the forced weather or the
    # roll (TutorSystem.TutorialMode). No ticks pass while it is swapped, so no incident can fire.
    sw=rb.call("jawa/storyteller_swap",{"storytellerDef":"Phoebe"}); out["swap"]=str(sw)[:300]; print("swap", str(sw)[:200])
    try:
        for w in ("RainyThunderstorm","Rain","FoggyRain"):
            s=rb.call("jawa/weather_set",{"weather":w,"lockWeather":True})
            r=rb.call("jawa/weather_roll_next",{})
            out[w]={"set_after":s.get("after"),"lockedTo":r.get("lockedTo"),"rolled":(r.get("after") or {}).get("weather")}; print(w, out[w])
        rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}); rb.call("jawa/weather_set",{"unlock":True})
        rolls=[]
        for i in range(40):
            r=rb.call("jawa/weather_roll_next",{}); rolls.append((r.get("after") or {}).get("weather"))
        from collections import Counter; out["unlocked_40"]=dict(Counter(rolls)); print("unlocked", out["unlocked_40"])
    finally:
        print("swap back", str(rb.call("jawa/storyteller_swap",{"storytellerDef":"Tutor"}))[:150])
        rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}); rb.call("jawa/safe_advance",{"ticks":60,"timeException":False})
        rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True})
json.dump(out, open(r"Transient\pv1\rain_postfix.json","w"), indent=1)
