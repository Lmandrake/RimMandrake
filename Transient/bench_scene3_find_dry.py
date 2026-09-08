import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
WATER = {"WaterDeep", "WaterOceanDeep", "WaterOceanShallow", "WaterShallow", "WaterMovingChestDeep", "WaterMovingShallow", "Marsh", "Mud"}
candidates = [(160,30,24,24),(160,75,24,24),(75,120,24,24),(120,120,24,24)]
with RimBridge(host, port, token) as rb:
    for x, z, w, h in candidates:
        corners = [(x,z),(x+w,z),(x,z+h),(x+w,z+h),(x+w//2,z+h//2)]
        terrains, fogged = [], []
        for cx, cz in corners:
            ci = rb.call("rimworld/get_cell_info", {"x": cx, "z": cz}).get("cell", {})
            terrains.append(ci.get("terrainDefName")); fogged.append(ci.get("fogged"))
        wet = [t for t in terrains if t in WATER]
        fog = [f for f in fogged if f]
        print(f"rect {x},{z},{w},{h} -> {terrains} fogged={fogged} {'WET' if wet else 'dry'} {'FOGGED' if fog else 'clear'}")
