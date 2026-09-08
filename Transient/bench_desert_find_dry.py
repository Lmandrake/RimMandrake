import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
WATER = {"WaterDeep", "WaterOceanDeep", "WaterOceanShallow", "WaterShallow", "WaterMovingChestDeep", "WaterMovingShallow", "Marsh", "Mud"}

candidates = [
    (40, 90, 24, 24),   # below waste_camp
    (70, 40, 20, 16),   # right of waste_camp
    (10, 90, 20, 16),   # lower-left
    (150, 150, 24, 24),
    (180, 60, 20, 16),
]

with RimBridge(host, port, token) as rb:
    for x, z, w, h in candidates:
        corners = [(x, z), (x + w, z), (x, z + h), (x + w, z + h), (x + w // 2, z + h // 2)]
        terrains = []
        for cx, cz in corners:
            ci = rb.call("rimworld/get_cell_info", {"x": cx, "z": cz})
            terrains.append(ci.get("cell", {}).get("terrainDefName"))
        wet = [t for t in terrains if t in WATER]
        print(f"rect {x},{z},{w},{h} -> terrains {terrains} {'WET' if wet else 'dry ok'}")
