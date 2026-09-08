import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=20) as rb:
    for x in range(107, 114):
        for z in range(105, 109):
            r = rb.call("rimworld/get_cell_info", {"x": x, "z": z})
            things = [t["defName"] for t in r["cell"]["things"]]
            if len(things) > 0 and things != []:
                interesting = [t for t in things if t not in ("Plant_Grass","Plant_TallGrass","Soil","Sand")]
                if interesting:
                    print(x, z, interesting)
