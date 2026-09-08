import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
WATER = {"WaterDeep", "WaterOceanDeep", "WaterOceanShallow", "WaterShallow", "WaterMovingChestDeep", "WaterMovingShallow", "Marsh", "Mud"}

candidates = [
    (100, 80, 24, 24),
    (140, 80, 24, 24),
    (95, 130, 24, 24),
    (140, 130, 24, 24),
]

with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})
    player = [p for p in pawns.get("pawns", []) if p.get("isPlayer")]
    print("player colonists:", [(p["name"], p["x"], p["z"]) for p in player])
    for x, z, w, h in candidates:
        corners = [(x, z), (x + w, z), (x, z + h), (x + w, z + h), (x + w // 2, z + h // 2)]
        terrains = []
        fogged = []
        for cx, cz in corners:
            ci = rb.call("rimworld/get_cell_info", {"x": cx, "z": cz}).get("cell", {})
            terrains.append(ci.get("terrainDefName"))
            fogged.append(ci.get("fogged"))
        wet = [t for t in terrains if t in WATER]
        print(f"rect {x},{z},{w},{h} -> terrains {terrains} fogged={fogged} {'WET' if wet else 'dry'}")
