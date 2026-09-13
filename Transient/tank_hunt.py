import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    t = rb.call("jawa/list_things", {"defName": "ChemfuelTank,LargeChemfuelTank,FuelStorage,MinifiedThing", "limit": 20})
    print("map-wide:", [(x["id"], x["x"], x["z"]) for x in t.get("things", [])])
    for cell in ("149,148", "149,151"):
        x, z = map(int, cell.split(","))
        r = rb.call("jawa/list_things", {"rect": f"{x},{z},1,1", "limit": 10})
        print(cell, "->", [(y["def"], y["id"]) for y in r.get("things", [])])
