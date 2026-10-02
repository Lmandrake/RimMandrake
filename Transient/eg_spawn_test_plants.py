import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

PLANTS = [
    ("Plant_Reeds", 15, 15, "Churn"),
    ("RG_Plant_AridGrass", 17, 15, "Burst"),
    ("RM_FE_Plant_Quickgrass", 19, 15, "Tinder"),
    ("AB_TallSlimyGrass", 21, 15, "Slime"),
    ("AB_AlienGrass", 23, 15, "Rupture"),
    ("AB_KeeningCordax", 25, 15, "Flush"),
]

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    results = []
    for defname, x, z, top in PLANTS:
        try:
            r = rb.call("rimworld/spawn_thing", {"defName": defname, "x": x, "z": z})
            results.append((defname, top, x, z, r.get("success"), r.get("thingId"), r.get("message")))
        except Exception as e:
            results.append((defname, top, x, z, "EXC", None, str(e)))
    for row in results:
        print(row)
