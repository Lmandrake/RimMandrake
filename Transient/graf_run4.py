import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=25) as rb:
    colonists = rb.call("rimworld/list_colonists", {})["colonists"]
    b = next(c for c in colonists if c["name"] == "Bundy")
    x, z = b["position"]["x"], b["position"]["z"]
    print("bundy at", x, z)
    for dx in range(-2, 3):
        r = rb.call("rimworld/spawn_thing", {"defName": "Wall", "x": x+dx, "z": z-3})
        print(dx, r.get("success"), r.get("thingId"))
