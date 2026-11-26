import json, sys
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
with RimBridge(h, p, tk) as rb:
    mi = rb.call("jawa/map_info", {}); print(mi.get("ticksGame"), mi.get("mapId"))
    f = rb.call("jawa/list_things", {"defName": "Fire", "limit": 2000}).get("things") or []
    print(len(f), [(x.get("x"), x.get("z")) for x in f][:12]); print(rb.call("jawa/weather_get", {}).get("weather"))
