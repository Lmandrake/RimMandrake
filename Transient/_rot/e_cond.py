import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/weather_set",{"weather":"RUT_SheenFall","lockWeather":True})
    print("weather_set:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:400])
    r=rb.call("jawa/game_condition",{"action":"start","condition":"RUT_SheenExposureLock","permanent":True})
    print("cond:", json.dumps({k:v for k,v in r.items() if k!="operation"})[:500])
    print("weather_get:", json.dumps(rb.call("jawa/weather_get",{}).get("weather"))[:300])
