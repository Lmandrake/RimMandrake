import sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
with RimBridge(h,p,tk) as rb:
    rb.call("jawa/map_fire",{"action":"extinguish","rect":"0,0,250,250"})
    print(rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}).get("after"))
    rb.call("jawa/safe_advance",{"ticks":60,"timeException":False})
    print(rb.call("jawa/weather_set",{"weather":"Clear","lockWeather":True}).get("after"))
