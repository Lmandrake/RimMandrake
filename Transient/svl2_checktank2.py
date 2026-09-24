import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    insp = rb.call("jawa/inspect_string", {"thingIds": "RSW_BactaTank692523"})
    print("TANK_INSPECT", json.dumps(insp)[:1500])
    bacta = rb.call("jawa/list_things", {"rect": "170,135,10,10", "limit": 10, "defName": "RSW_Bacta"})
    print("BACTA_LEFT", json.dumps(bacta)[:800])
